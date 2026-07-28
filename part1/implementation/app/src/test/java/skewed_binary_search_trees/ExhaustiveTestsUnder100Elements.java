package skewed_binary_search_trees;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

import java.util.Optional;
import java.util.Set;
import java.util.stream.Collectors;
import java.util.stream.IntStream;

public class ExhaustiveTestsUnder100Elements {

    private static final double[] ALPHA_VALUES = { 0.25, 0.5, 0.75 };

    private static Set<Integer> createConsecutiveSet(int size) {
        return IntStream.range(0, size)
                .boxed()
                .collect(Collectors.toSet());
    }

    private static Set<Integer> createSpacedSet(int size) {
        return IntStream.range(0, size)
                .map(i -> i * 2) // Elements are 0, 2, 4, 6, ...
                .boxed()
                .collect(Collectors.toSet());
    }

    abstract static class SearchStrategyCorrectnessTests {

        protected abstract SearchStrategy createStrategy(Set<Integer> numbers, double alpha);

        protected abstract String getImplementationName();

        @Test
        void givenQueryEqualsElement_returnElement() {
            for (int size = 1; size < 100; size++) {
                Set<Integer> elements = createConsecutiveSet(size);

                for (double alpha : ALPHA_VALUES) {
                    SearchStrategy structure = createStrategy(elements, alpha);

                    for (int element : elements) {
                        Optional<Integer> result = structure.pred(element);
                        assertTrue(result.isPresent(),
                                String.format("%s: Size=%d, alpha=%.2f: pred(%d) should not be empty",
                                        getImplementationName(), size, alpha, element));
                        assertEquals(element, result.get(),
                                String.format("%s: Size=%d, alpha=%.2f: pred(%d) should return %d",
                                        getImplementationName(), size, alpha, element, element));
                    }
                }
            }
        }

        @Test
        void givenQueryBiggerThanElement_returnsNearestSmallerElement() {
            for (int size = 1; size < 100; size++) {
                Set<Integer> elements = createSpacedSet(size); // 0, 2, 4, ...

                for (double alpha : ALPHA_VALUES) {
                    SearchStrategy structure = createStrategy(elements, alpha);

                    // Query odd numbers - they fall between consecutive elements
                    for (int i = 0; i < size - 1; i++) {
                        int element = i * 2; // Current element (e.g., 0, 2, 4)
                        int queryBetween = element + 1; // Query between (e.g., 1, 3, 5)

                        Optional<Integer> result = structure.pred(queryBetween);
                        assertTrue(result.isPresent(),
                                String.format("%s: Size=%d, alpha=%.2f: pred(%d) should not be empty",
                                        getImplementationName(), size, alpha, queryBetween));
                        assertEquals(element, result.get(),
                                String.format("%s: Size=%d, alpha=%.2f: pred(%d) should return %d",
                                        getImplementationName(), size, alpha, queryBetween, element));
                    }
                }
            }
        }

        @Test
        void givenQueryBelowMinimumElement_returnsEmpty() {
            for (int size = 1; size < 100; size++) {
                // Use elements starting from 10 so we can query below
                Set<Integer> elements = IntStream.range(10, 10 + size)
                        .boxed()
                        .collect(Collectors.toSet());

                for (double alpha : ALPHA_VALUES) {
                    SearchStrategy structure = createStrategy(elements, alpha);

                    int queryBelowMin = 9; // Below minimum element (10)

                    assertTrue(structure.pred(queryBelowMin).isEmpty(),
                            String.format("%s: Size=%d, alpha=%.2f: pred(%d) should be empty",
                                    getImplementationName(), size, alpha, queryBelowMin));
                }
            }
        }

        @Test
        void givenQueryAboveMaximumElement_returnsMaximumElement() {
            for (int size = 1; size < 100; size++) {
                Set<Integer> elements = createConsecutiveSet(size); // 0 to size-1
                int maxElement = size - 1;

                for (double alpha : ALPHA_VALUES) {
                    SearchStrategy structure = createStrategy(elements, alpha);

                    int queryAboveMax = maxElement + 100; // Well above maximum

                    assertEquals(Optional.of(maxElement), structure.pred(queryAboveMax),
                            String.format("%s: Size=%d, alpha=%.2f: pred(%d) should return %d",
                                    getImplementationName(), size, alpha, queryAboveMax, maxElement));
                }
            }
        }

        static class SortedArrayCorrectnessTests extends SearchStrategyCorrectnessTests {
            @Override
            protected SearchStrategy createStrategy(Set<Integer> numbers, double alpha) {
                return new SortedArray(numbers, alpha);
            }

            @Override
            protected String getImplementationName() {
                return "SortedArray";
            }
        }

        static class SearchTreeCorrectnessTests extends SearchStrategyCorrectnessTests {
            @Override
            protected SearchStrategy createStrategy(Set<Integer> numbers, double alpha) {
                return new SearchTree(numbers, alpha);
            }

            @Override
            protected String getImplementationName() {
                return "SearchTree";
            }
        }

        static class OtherArrayCorrectnessTests extends SearchStrategyCorrectnessTests {
            @Override
            protected SearchStrategy createStrategy(Set<Integer> numbers, double alpha) {
                return new OtherArray(numbers, alpha);
            }

            @Override
            protected String getImplementationName() {
                return "OtherArray";
            }
        }

        @Test
        void givenQueries_allImplementationsReturnSameResult() {
            for (int size = 1; size < 100; size++) {
                Set<Integer> elements = createSpacedSet(size); // 0, 2, 4, ...
                int maxElement = (size - 1) * 2;

                for (double alpha : ALPHA_VALUES) {
                    SortedArray sortedArray = new SortedArray(elements, alpha);
                    SearchTree searchTree = new SearchTree(elements, alpha);
                    OtherArray otherArray = new OtherArray(elements, alpha);

                    // Test all queries from below minimum to above maximum
                    for (int query = -1; query <= maxElement + 2; query++) {
                        Optional<Integer> resultSorted = sortedArray.pred(query);
                        Optional<Integer> resultTree = searchTree.pred(query);
                        Optional<Integer> resultOther = otherArray.pred(query);

                        assertEquals(resultSorted, resultTree,
                                String.format("Size=%d, alpha=%.2f, query=%d: SortedArray and SearchTree differ",
                                        size, alpha, query));
                        assertEquals(resultSorted, resultOther,
                                String.format("Size=%d, alpha=%.2f, query=%d: SortedArray and OtherArray differ",
                                        size, alpha, query));
                    }
                }
            }
        }
    }
}