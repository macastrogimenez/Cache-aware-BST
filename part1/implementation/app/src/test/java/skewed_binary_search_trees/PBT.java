package skewed_binary_search_trees;

import java.util.Comparator;
import java.util.HashSet;
import java.util.Set;

import net.jqwik.api.Arbitraries;
import net.jqwik.api.Arbitrary;
import net.jqwik.api.Combinators;
import net.jqwik.api.ForAll;
import net.jqwik.api.Property;
import net.jqwik.api.Provide;
import net.jqwik.api.Tuple;
import net.jqwik.api.constraints.DoubleRange;
import net.jqwik.api.constraints.IntRange;
import net.jqwik.api.constraints.Size;

public class PBT {

    // Oracle test: All implementations should produce the same result
    @Property
    void allImplementationsProduceSameResult(
            @ForAll @Size(min = 1) Set<Integer> numbers,
            @ForAll int query,
            @ForAll @DoubleRange(min = 0, max = 1, minIncluded = false, maxIncluded = false) double alfa) {
        
        var sortedArray = new SortedArray(numbers, alfa);
        var searchTree = new SearchTree(numbers, alfa);
        var otherArray = new OtherArray(numbers, alfa);
        
        var sortedArrayResult = sortedArray.pred(query);
        var searchTreeResult = searchTree.pred(query);
        var otherArrayResult = otherArray.pred(query);
        
        // All implementations should produce the same result
        assert sortedArrayResult.equals(searchTreeResult) : 
            String.format("SortedArray and SearchTree differ for query %d: %s vs %s", 
                query, sortedArrayResult, searchTreeResult);
        assert sortedArrayResult.equals(otherArrayResult) : 
            String.format("SortedArray and OtherArray differ for query %d: %s vs %s", 
                query, sortedArrayResult, otherArrayResult);
    }

    abstract static class SearchStrategyTests {

        protected abstract SearchStrategy createStrategy(Set<Integer> numbers, double alfa);

        // Pred(x) = max{y ∈ S | y ≤ x}
        @Property
        void predMatchesDefinition(
                @ForAll @Size(min = 1) Set<Integer> numbers,
                @ForAll int query,
                @ForAll @DoubleRange(min = 0, max = 1, minIncluded = false, maxIncluded = false) double alfa) {
            var array = createStrategy(numbers, alfa);
            var result = array.pred(query);

            if (result.isEmpty())
                return;

            // y ≤ x
            assert result.get() <= query;

            // y ∈ S
            assert numbers.contains(result.get());

            for (int i : numbers) {
                if (i == result.get())
                    continue;

                // All other elements must be larger than the query,
                // or smaller than the result
                assert i > query || i < result.get();
            }
        }

        @Property
        void anyQueryLowerThanTheSmallestElementIsUndefined(
                // MIN_VALUE + 1 so that we can get a query that's smaller than the smallest
                // element in the input set
                @ForAll @Size(min = 1) Set<@IntRange(min = Integer.MIN_VALUE + 1) Integer> numbers,
                @ForAll @DoubleRange(min = 0, max = 1, minIncluded = false, maxIncluded = false) double alfa) {

            // - 1 so that the query is smaller than the smallest element
            int query = numbers.stream().min(Comparator.naturalOrder()).get() - 1;
            var array = createStrategy(numbers, alfa);
            var result = array.pred(query);

            assert result.isEmpty();
        }

        @Property
        void anyQueryLargerThanTheLargestElementIsTheLargestElement(
                // MAX_VALUE - 1 so that we can get a query that's larger than the largest
                // element in the input set
                @ForAll @Size(min = 1) Set<@IntRange(max = Integer.MAX_VALUE - 1) Integer> numbers,
                @ForAll @DoubleRange(min = 0, max = 1, minIncluded = false, maxIncluded = false) double alfa) {

            // + 1 so that the query is larger than the largest element
            int largestElement = numbers.stream().max(Comparator.naturalOrder()).get();
            int query = largestElement + 1;
            var array = createStrategy(numbers, alfa);
            var result = array.pred(query);

            assert result.isPresent();
            assert result.get() == largestElement;
        }

        private record InsertionTestData(Set<Integer> numbers, double alfa, int query, int elementToInsert) {
        }

        // We are generating arbitraries that will never produce null values
        @SuppressWarnings("null")
        @Provide
        Arbitrary<InsertionTestData> queryWithLargerElement() {
            Arbitrary<Double> alfa = Arbitraries.doubles().between(0.0, false, 1.0, false);
            Arbitrary<Set<Integer>> numbers = Arbitraries.integers().set().ofMinSize(1);

            var queryAndElement = Arbitraries.integers().lessOrEqual(Integer.MAX_VALUE - 1)
                    .flatMap(query -> Arbitraries.integers().greaterOrEqual(query + 1)
                            .map(elementToInsert -> Tuple.of(query, elementToInsert)));

            return Combinators.combine(numbers, alfa, queryAndElement)
                    .as((n, a, qe) -> new InsertionTestData(n, a, qe.get1(), qe.get2()));
        }

        @Property
        void resultDoesNotChangeWhenElementLargerThanQueryIsInserted(
                @ForAll("queryWithLargerElement") InsertionTestData data) {
            var array = createStrategy(data.numbers, data.alfa);
            var initialResult = array.pred(data.query);

            var modifiedNumbers = new HashSet<>(data.numbers);
            modifiedNumbers.add(data.elementToInsert);

            var modifiedArray = createStrategy(modifiedNumbers, data.alfa);
            var newResult = modifiedArray.pred(data.query);

            assert initialResult.equals(newResult);
        }

        private record CloserElementTestData(
                Set<Integer> numbers, double alfa, int query, int currentPred, int elementToInsert) {
        }

        /**
         * Generates test data for verifying predecessor behavior when a closer element
         * is inserted.
         *
         * <p>
         * This provider creates scenarios where:
         * <ul>
         * <li>{@code currentPred} is the current predecessor of the query in the
         * initial set</li>
         * <li>{@code elementToInsert} is strictly between {@code currentPred} and
         * {@code query}</li>
         * <li>All other elements in {@code numbers} are strictly less than
         * {@code currentPred}</li>
         * </ul>
         *
         * <p>
         * The invariants guaranteed by this generator:
         * 
         * <pre>
         *   ∀x ∈ (numbers \ {currentPred}): x < currentPred
         *   currentPred < elementToInsert ≤ query
         * </pre>
         *
         * <p>
         * This setup ensures that after inserting {@code elementToInsert}, the
         * predecessor
         * of {@code query} must change from {@code currentPred} to a value closer to
         * the query.
         *
         * @return an arbitrary producing {@link CloserElementTestData} instances with
         *         the above constraints
         */
        @SuppressWarnings("null") // Generated arbitraries never produce null values
        @Provide
        Arbitrary<CloserElementTestData> queryWithCloserElement() {
            var alfa = Arbitraries.doubles().between(0.0, false, 1.0, false);

            var dependentParts = Arbitraries.integers().between(Integer.MIN_VALUE + 1, Integer.MAX_VALUE - 2)
                    .flatMap(currentPred -> Arbitraries.integers().between(currentPred + 1, Integer.MAX_VALUE)
                            .flatMap(query -> Arbitraries.integers().between(currentPred + 1, query)
                                    .flatMap(
                                            elementToInsert -> Arbitraries.integers().lessOrEqual(currentPred - 1).set()
                                                    .map(others -> {
                                                        var numbers = new java.util.HashSet<>(others);
                                                        numbers.add(currentPred);
                                                        return Tuple.of(numbers, query, currentPred, elementToInsert);
                                                    }))));

            return Combinators.combine(alfa, dependentParts)
                    .as((a, dp) -> new CloserElementTestData(dp.get1(), a, dp.get2(), dp.get3(), dp.get4()));
        }

        @Property
        void resultChangesWhenElementBetweenCurrentPredAndQueryIsInserted(
                @ForAll("queryWithCloserElement") CloserElementTestData data) {
            var array = createStrategy(data.numbers, data.alfa);
            var initialResult = array.pred(data.query);

            var modifiedNumbers = new HashSet<>(data.numbers);
            modifiedNumbers.add(data.elementToInsert);

            var newArray = createStrategy(modifiedNumbers, data.alfa);
            var newResult = newArray.pred(data.query);

            assert initialResult.get() != newResult.get();
            assert newResult.get() > initialResult.get();
        }
    }

    static class SortedArrayTests extends SearchStrategyTests {
        @Override
        protected SearchStrategy createStrategy(Set<Integer> numbers, double alfa) {
            return new SortedArray(numbers, alfa);
        }
    }

    static class SearchTreeTests extends SearchStrategyTests {
        @Override
        protected SearchStrategy createStrategy(Set<Integer> numbers, double alfa) {
            return new SearchTree(numbers, alfa);
        }
    }

    static class OtherArrayTests extends SearchStrategyTests {
        @Override
        protected SearchStrategy createStrategy(Set<Integer> numbers, double alfa) {
            return new OtherArray(numbers, alfa);
        }
    }
}
