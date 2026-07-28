package skewed_binary_search_trees;

import java.util.HashSet;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;
import java.util.Optional;

public class OtherArrayNaiveTest {
    HashSet<Integer> set;
    OtherArray a;
    
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
    void OtherArrayWithAlphaZeroFive(){
        a = new OtherArray(set, 0.5);
        assertEquals(Optional.of(11), a.pred(12));
    }

    @Test
    void OtherArrayWithAlphaZeroFour(){
        a = new OtherArray(set, 0.4);
        assertEquals(Optional.of(11), a.pred(12));
    }

    @Test
    void OtherArrayWithAlphaZeroThree(){
        a = new OtherArray(set, 0.3);
        assertEquals(Optional.of(11), a.pred(12));
    }
    
    @Test
    void OtherArrayWithExactPredSearch(){
        a = new OtherArray(set, 0.3);
        assertEquals(Optional.of(13), a.pred(13));
    }

    // When looking for 
    @Test
    void OtherArrayWithNoPredButExistingElement(){
        a = new OtherArray(set, 0.3);
        assertEquals(Optional.of(2), a.pred(2));
    }

    @Test
    void OtherArrayWithNoPredNonExistingE(){
        a = new OtherArray(set, 0.3);
        assertEquals(Optional.empty(), a.pred(-1));
    }

    @Test
    void OtherArrayPredLargerThanMax(){
        a = new OtherArray(set, 0.3);
        assertEquals(Optional.of(13), a.pred(15));
    }
}


