package skewed_binary_search_trees;

import java.util.HashSet;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;
import java.util.Optional;

public class SearchTreeNaiveTest {
    HashSet<Integer> set;
    SearchTree a;
    
    @BeforeEach
    void setUp(){
        this.set = new HashSet<Integer>();
        
        set.add(2);
        set.add(5); 
        set.add(8);
        set.add(11);
        set.add(13);
    }    
    
    @Test
    void SortedArrayWithAlphaZeroFive(){
        a = new SearchTree(set, 0.5);
        assertEquals(Optional.of(11), a.pred(12));
    }

    @Test
    void SortedArrayWithAlphaZeroFour(){
        a = new SearchTree(set, 0.4);
        assertEquals(Optional.of(11), a.pred(12));
    }

    @Test
    void SortedArrayWithAlphaZeroThree(){
        a = new SearchTree(set, 0.3);
        assertEquals(Optional.of(11), a.pred(12));
    }
    
    @Test
    void SortedArrayWithExactPredSearch(){
        a = new SearchTree(set, 0.3);
        assertEquals(Optional.of(13), a.pred(13));
    }

    @Test
    void SortedArrayWithNoPredButExistingElement(){
        a = new SearchTree(set, 0.3);
        assertEquals(Optional.of(2), a.pred(2));
    }

    @Test
    void SortedArrayWithNoPredNonExistingE(){
        a = new SearchTree(set, 0.3);
        assertEquals(Optional.empty(), a.pred(-1));
    }


    

    
        
}
