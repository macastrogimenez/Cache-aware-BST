package rank_select;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

public class RankSelectNaiveTest {

    @Test
    void testRankSmallVector() {
        int[] vector = {1, 0, 1, 1};
        RankSelectNaive rs = new RankSelectNaive(vector);

        assertEquals(1, rs.rank(0));
        assertEquals(1, rs.rank(1));
        assertEquals(2, rs.rank(2));
        assertEquals(3, rs.rank(3));
    }

    @Test
    void testRankAllZeros() {
        int[] vector = {0, 0, 0};
        RankSelectNaive rs = new RankSelectNaive(vector);

        assertEquals(0, rs.rank(0));
        assertEquals(0, rs.rank(1));
        assertEquals(0, rs.rank(2));
    }

    @Test
    void testSelectSmallVector() {
        int[] vector = {1, 0, 1, 1};
        RankSelectNaive rs = new RankSelectNaive(vector);

        assertEquals(0, rs.select(1)); // first 1
        assertEquals(2, rs.select(2)); // second 1
        assertEquals(3, rs.select(3)); // third 1
        assertEquals(-1, rs.select(4)); // nonexistent
    }

    @Test
    void testSelectAllZeros() {
        int[] vector = {0, 0, 0, 0};
        RankSelectNaive rs = new RankSelectNaive(vector);

        assertEquals(-1, rs.select(1));
        assertEquals(-1, rs.select(2));
    }

    @Test
    void testSelectZeroOrNegative() {
        int[] vector = {1, 0, 1};
        RankSelectNaive rs = new RankSelectNaive(vector);

        assertEquals(-1, rs.select(0));
        assertEquals(-1, rs.select(-5));
    }
}

