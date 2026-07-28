package rank_select;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

public class RankSelectLookupTest {

    @Test
    void testPrecomputation() {
        int[] vector = new int[64];
        // repeating pattern: 1,0,1,0,...
        for (int i = 0; i < vector.length; i++) {
            vector[i] = (i % 2 == 0) ? 1 : 0;
        }
        RankSelectLookup rs = new RankSelectLookup(vector);

        assertEquals(1, rs.R[0], "R[0] should be 1");
        assertEquals(16, rs.R[31], "R[31] should be 16");
        assertEquals(32, rs.R[63], "R[63] should be 32");
    }

    @Test
    void testRankFunction() {
        int[] vector = new int[64];
        for (int i = 0; i < vector.length; i++) {
            vector[i] = (i % 2 == 0) ? 1 : 0;
        }
        RankSelectLookup rs = new RankSelectLookup(vector);

        assertEquals(1, rs.rank(0), "rank(0) should be 1");
        assertEquals(16, rs.rank(31), "rank(31) should be 16");
        assertEquals(32, rs.rank(63), "rank(63) should be 32");
    }

    @Test
    void testSelectFunctionBasic() {
        int[] vector = {1, 0, 1, 1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 1, 0}; 
        RankSelectLookup rs = new RankSelectLookup(vector);

        assertEquals(0, rs.select(1), "select(1) should return index 0");
        assertEquals(2, rs.select(2), "select(2) should return index 2");
        assertEquals(3, rs.select(3), "select(3) should return index 3");
        assertEquals(5, rs.select(4), "select(4) should return index 5");
    }

    @Test
    void testSelectReturnsFirstOccurrence() {
        int[] vector = {1, 0, 1, 1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 1, 0};
        RankSelectLookup rs = new RankSelectLookup(vector);


        assertEquals(0, rs.select(1), "select should return earliest index where R[i] >= r");
        assertEquals(3, rs.select(3), "select should return first index with cumulative rank 3");
    }

    @Test
    void testSelectForNonExistentRank() {
        int[] vector = {1, 0, 1, 1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 1, 0};
        RankSelectLookup rs = new RankSelectLookup(vector);

        assertEquals(-1, rs.select(50), "select(50) should return -1 because total ones = 4");
        assertEquals(-1, rs.select(70), "select(70) should return -1 for out-of-range r");
    }

    @Test
    void testSelectZeroOrNegative() {
        int[] vector = {1, 0, 1, 1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 1, 0};
        RankSelectLookup rs = new RankSelectLookup(vector);

        assertEquals(-1, rs.select(0), "select(0) should return -1 (rank values start at 1)");
        assertEquals(-1, rs.select(-2), "select(-2) should return -1");
    }

    @Test
    void testSelectOnVectorWithNoOnes() {
        int[] vector = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0};
        RankSelectLookup rs = new RankSelectLookup(vector);

        assertEquals(-1, rs.select(1),
                "select should return -1 when vector contains no ones");
    }
}
