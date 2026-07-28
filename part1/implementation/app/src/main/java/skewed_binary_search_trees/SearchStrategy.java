package skewed_binary_search_trees;
import java.util.Optional;

public interface SearchStrategy{
    public Optional<Integer> pred(int x);
}
