package skewed_binary_search_trees;


import java.util.Set;
import java.util.Optional;

public class SortedArray implements SearchStrategy {
    int[] sortedArray;
    double alpha;
    int root;

    public SortedArray(Set<Integer> ints, double alpha) {
        this.sortedArray = ints.stream()
            .sorted()   
            .mapToInt(Integer::intValue)
            .toArray();  
        
        if (alpha <= 0.00 || alpha >= 1.00) {
            throw new IllegalArgumentException("Alpha cannot be lower than 0 or higher than 1");
        }
        else {
            this.alpha = alpha;
        }
    };

    //Checks if x is smaller than the smallest value in the set -> in that case returns Optional[Nullable]
        // else ->  calls recursive method predHelper() with initial values as 
            // the sortedArray as the collection to check
            // x: value to check pred for
            // left index: 0 (beginning of the array)
            // right index: last index of the array
            // best value so far: null - which can be returned in case of no find
    @Override
    public Optional<Integer> pred(int x) {
        if(sortedArray[0]>x){
            return Optional.ofNullable(null);    
        }
        Integer value = predHelper(sortedArray, x, 0, sortedArray.length - 1, null);
        return Optional.ofNullable(value);
    }

    // recursive method which traverses the array in skewed BST fashion
        // we declare the mid (the first mid would be the root) of the array as the index it would be * alpha (rounded down)
            // is mid = x? -> true, return mid
            // is mid lower than x -> go higher (go right), recursively with predHelper(), 
                // search from left = mid+1 until previous right = right value
            // if mid higher than x -> go lower (go left), recursively with predHelper(), 
                // search from left = previous left to right = mid - 1
    private int predHelper(int[] A, int x, int left, int right, Integer best) {

        if (left > right) {
            return best;
        }

        // we declare the mid (the first mid would be the root) of the array as the index it would be * alpha (rounded down)
        int mid = left + (int) Math.floor((right - left) * alpha);

        // is mid = x? -> true, return mid
        if (A[mid] == x) {
            return A[mid];  // exact match → this IS the floor
        }

        // is mid lower than x -> go higher (go right), recursively with predHelper(), 
        // search from left = mid+1 until previous right = right value
        if (A[mid] < x) {
            // A[mid] is a valid floor candidate → update best and search right half
            return predHelper(A, x, mid + 1, right, A[mid]);
        }
        // if mid higher than x -> go lower (go left), recursively with predHelper(), search from left = previous left to right = mid - 1
        else {
            // A[mid] > x → search the left half
            return predHelper(A, x, left, mid - 1, best);
        }
    }
    


    // public int pred(int x) {
    //     throw new UnsupportedOperationException("Not implemented");
    // }

    // public static void main(String[] args) {
    //     HashSet<Integer> set = new HashSet<Integer>();
    //     //IntStream.range(0, 10).forEach(a ->set.add(a));

    //     set.add(2);
    //     set.add(5);
    //     set.add(8);
    //     set.add(11);
    //     set.add(13);
        
    //     SortedArray a = new SortedArray(set, 0.3);
    //     System.out.println(a.pred(12));
    // }
}
