package rank_select;

import java.util.Arrays;

import net.jqwik.api.Arbitraries;
import net.jqwik.api.Arbitrary;
import net.jqwik.api.Assume;
import net.jqwik.api.ForAll;
import net.jqwik.api.Property;
import net.jqwik.api.Provide;
import net.jqwik.api.constraints.IntRange;

public class PBT {
    record ArrayWithR(int[] vector, int r) {
    }

    record ArrayWithIJ(int[] vector, int i, int j) {
    }

    record ZeroArrayWithR(int[] vector, int r) {
    }

    record OnesArrayWithR(int[] vector, int r) {
    }

    @Provide
    Arbitrary<int[]> binaryArray() {
        // 15 chosen arbitrarily for speed of test suite
        return Arbitraries.integers().between(6, 15)
                .map(power -> 1 << power)
                .flatMap(size -> Arbitraries.integers().between(0, 1).array(int[].class).ofSize(size));
    }

    /**
     * Generates binaryArray with arbitrary size and {@code r},
     * guaranteed to fulfil {@code 0 <= r <= countOfOnesInArray}
     */
    @Provide
    Arbitrary<ArrayWithR> binaryArrayWithR() {
        // 15 chosen arbitrarily for speed of test suite
        return Arbitraries.integers().between(6, 15)
                .map(power -> 1 << power)
                .flatMap(size -> Arbitraries.integers().between(0, 1).array(int[].class).ofSize(size))
                .flatMap(array -> {
                    int onesCount = (int) Arrays.stream(array).filter(x -> x == 1).count();
                    if (onesCount == 0) {
                        return Arbitraries.just(new ArrayWithR(array, 0));
                    }
                    return Arbitraries.integers().between(1, onesCount)
                            .map(r -> new ArrayWithR(array, r));
                });
    }

    // Oracle test: All implementations should produce the same result
    @Property
    void selectAllImplementationsProduceSameResult(@ForAll("binaryArrayWithR") ArrayWithR data,
            // 1 through 30 chosen arbitrarily just to avoid depending on a specific k
            @ForAll @IntRange(min = 1, max = 30) int k) {
        var rsNaive = new RankSelectNaive(data.vector);
        var rsLookup = new RankSelectLookup(data.vector);
        var rsSpaceEfficient = new RankSelectSpaceEfficient(data.vector, k);

        assert rsNaive.select(data.r) == rsLookup.select(data.r);
        assert rsNaive.select(data.r) == rsSpaceEfficient.select(data.r);
    }

    abstract static class RankSelectStrategyTests {

        protected abstract RankSelectStrategy createStrategy(int[] vector, int k);

        @Provide
        Arbitrary<int[]> binaryArray() {
            // 15 chosen arbitrarily for speed of test suite
            return Arbitraries.integers().between(6, 15)
                    .map(power -> 1 << power)
                    .flatMap(size -> Arbitraries.integers().between(0, 1).array(int[].class).ofSize(size));
        }

        /**
         * Generates binaryArray with arbitrary size and {@code r},
         * guaranteed to fulfil {@code 0 <= r <= countOfOnesInArray}
         */
        @Provide
        Arbitrary<ArrayWithR> binaryArrayWithR() {
            // 15 chosen arbitrarily for speed of test suite
            return Arbitraries.integers().between(6, 15)
                    .map(power -> 1 << power)
                    .flatMap(size -> Arbitraries.integers().between(0, 1).array(int[].class).ofSize(size))
                    .flatMap(array -> {
                        int onesCount = (int) Arrays.stream(array).filter(x -> x == 1).count();
                        if (onesCount == 0) {
                            return Arbitraries.just(new ArrayWithR(array, 0));
                        }
                        return Arbitraries.integers().between(1, onesCount)
                                .map(r -> new ArrayWithR(array, r));
                    });
        }

        /**
         * Generates binaryArray with arbitrary size and {@code r},
         * guaranteed to fulfil {@code 0 <= i < j <= countOfOnesInArray}
         */
        @Provide
        Arbitrary<ArrayWithIJ> binaryArrayWithIJ() {
            // 15 chosen arbitrarily for speed of test suite
            return Arbitraries.integers().between(6, 15)
                    .map(power -> 1 << power)
                    .flatMap(size -> Arbitraries.integers().between(0, 1).array(int[].class).ofSize(size))
                    .flatMap(array -> {
                        int onesCount = (int) Arrays.stream(array).filter(x -> x == 1).count();
                        if (onesCount < 2) {
                            return Arbitraries.just(new ArrayWithIJ(array, 0, 0));
                        }
                        return Arbitraries.integers().between(0, onesCount - 2)
                                .flatMap(i -> Arbitraries.integers().between(i + 1, onesCount - 1)
                                        .map(j -> new ArrayWithIJ(array, i, j)));
                    });
        }

        @Provide
        Arbitrary<ZeroArrayWithR> arrayZeros() {
            return Arbitraries.integers().between(6, 15)
                    .map(power -> 1 << power)
                    .flatMap(size -> Arbitraries.integers().between(0, 0).array(int[].class).ofSize(size))
                    .flatMap(array -> {
                        return Arbitraries.integers().between(1, array.length)
                                .map(r -> new ZeroArrayWithR(array, r));
                    });
        }

        @Provide
        Arbitrary<OnesArrayWithR> arrayOnes() {
            return Arbitraries.integers().between(6, 15)
                    .map(power -> 1 << power)
                    .flatMap(size -> Arbitraries.integers().between(1, 1).array(int[].class).ofSize(size))
                    .flatMap(array -> {
                        return Arbitraries.integers().between(1, array.length)
                                .map(r -> new OnesArrayWithR(array, r));
                    });
        }

        // Rank(Select(r)) == r
        @Property
        void selectThenRankReturnsInput(@ForAll("binaryArrayWithR") ArrayWithR data,
                @ForAll @IntRange(min = 1, max = 30) int k) {
            int[] vector = data.vector;
            int r = data.r();

            Assume.that(Arrays.stream(vector).anyMatch(x -> x == 1));
            Assume.that(r > 0);

            var rs = createStrategy(vector, k);

            assert rs.rank(rs.select(r)) == r;
        }

        @Property
        void selectIsStrictlyIncreasing(
                @ForAll("binaryArrayWithR") ArrayWithR data,
                @ForAll @IntRange(min = 1, max = 30) int k) {
            Assume.that(Arrays.stream(data.vector).filter(x -> x == 1).count() > 2);
            Assume.that(data.r > 2);

            var rs = createStrategy(data.vector, k);

            assert rs.select(data.r - 1) < rs.select(data.r);
        }

        @Property
        void rankIsNonDecreasing(@ForAll("binaryArrayWithIJ") ArrayWithIJ data,
                @ForAll @IntRange(min = 1, max = 30) int k) {
            Assume.that(data.i != 0 && data.j != 0);

            var rs = createStrategy(data.vector, k);

            assert rs.rank(data.i) <= rs.rank(data.j);
        }

        @Property
        void rankZeroReturnsFirstBit(@ForAll("binaryArray") int[] vector,
                @ForAll @IntRange(min = 1, max = 30) int k) {
            var rs = createStrategy(vector, k);

            assert rs.rank(0) == vector[0];
        }

        @Property
        void rankAtUpperEdgeReturnsTotalCountOfOnes(@ForAll("binaryArray") int[] vector,
                @ForAll @IntRange(min = 1, max = 30) int k) {
            var onesCount = Arrays.stream(vector).filter(x -> x == 1).count();
            var rs = createStrategy(vector, k);

            assert rs.rank(vector.length - 1) == onesCount;
        }

        @Property
        void selectReturnsNotFoundForAllZeros(@ForAll("arrayZeros") ZeroArrayWithR data,
                @ForAll @IntRange(min = 1, max = 30) int k) {
            var rs = createStrategy(data.vector, k);

            assert rs.select(data.r) == -1;
        }

        @Property
        void selectReturnsTheIndexMinusOneForAllOnes(@ForAll("arrayOnes") OnesArrayWithR data,
                @ForAll @IntRange(min = 1, max = 30) int k) {
            var rs = createStrategy(data.vector, k);

            assert rs.select(data.r) == data.r - 1;
        }

        @Property
        void selectResultIsAlwaysSmallerThanSizeOfVector(@ForAll("binaryArrayWithR") ArrayWithR data,
                @ForAll @IntRange(min = 1, max = 30) int k) {
            var rs = createStrategy(data.vector, k);

            assert rs.select(data.r) < data.vector.length;
        }
    }

    static class RankSelectNaiveTests extends RankSelectStrategyTests {
        @Override
        protected RankSelectStrategy createStrategy(int[] vector, int k) {
            return new RankSelectNaive(vector);
        }
    }

    static class RankSelectLookupTests extends RankSelectStrategyTests {
        @Override
        protected RankSelectStrategy createStrategy(int[] vector, int k) {
            return new RankSelectLookup(vector);
        }
    }

    static class RankSelectSpaceEfficientTests extends RankSelectStrategyTests {
        @Override
        protected RankSelectStrategy createStrategy(int[] vector, int k) {
            return new RankSelectSpaceEfficient(vector, k);
        }
    }
}
