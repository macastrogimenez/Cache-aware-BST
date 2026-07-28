package rank_select;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import java.util.*;

public class SelectSpaceEfficientSelectTest {

    // Helper: get all 1 positions in the vector
    private List<Integer> getPositions(int[] vector) {
        List<Integer> pos = new ArrayList<>();
        for (int i = 0; i < vector.length; i++) {
            if (vector[i] == 1) pos.add(i);
        }
        return pos;
    }

    @Test
    public void testSimplePattern() {
        int[] vector = {
            1,0,1,0,1,0,1,0,
            1,0,1,0,1,0,1,0,
            1,0,1,0,1,0,1,0,
            1,0,1,0,1,0,1,0,
            1,0,1,0,1,0,1,0,
            1,0,1,0,1,0,1,0,
            1,0,1,0,1,0,1,0,
            1,0,1,0,1,0,1,0
        }; // length 64

        System.out.println("simple");
        RankSelectSpaceEfficient rs = new RankSelectSpaceEfficient(vector, 2);

        List<Integer> ones = getPositions(vector);

        for (int r = 1; r <= ones.size(); r++) {
            assertEquals(ones.get(r-1).intValue(), rs.select(r), 
                "select(" + r + ") failed");
        }
    }

    @Test
    public void testAllZeros() {
        int n = 64;
        int[] vector = new int[n];
        System.out.println("0");
        RankSelectSpaceEfficient rs = new RankSelectSpaceEfficient(vector, 2);

        for (int r = 1; r <= 10; r++) {
            assertEquals(-1, rs.select(r), "select on all-zero vector must be -1");
        }
    }

    @Test
    public void testAllOnes() {
        int n = 64;
        int[] vector = new int[n];
        System.out.println("1");
        for (int i = 0; i < n; i++) vector[i] = 1;

        RankSelectSpaceEfficient rs = new RankSelectSpaceEfficient(vector, 2);

        for (int r = 1; r <= n; r++) {
            assertEquals(r - 1, rs.select(r), 
                "select(" + r + ") should return " + (r - 1));
        }

        assertEquals(-1, rs.select(n + 1), "Out-of-range select must be -1");
    }

    @Test
    public void testAlternatingBits() {
        int n = 128;
        int[] vector = new int[n];
        for (int i = 0; i < n; i++) vector[i] = i % 2;

        RankSelectSpaceEfficient rs = new RankSelectSpaceEfficient(vector, 2);

        List<Integer> ones = getPositions(vector);

        for (int r = 1; r <= ones.size(); r++) {
            assertEquals(ones.get(r - 1).intValue(), rs.select(r));
        }
    }

    @Test
    public void testSingleOneAtEnd() {
        int n = 64;
        int[] vector = new int[n];
        vector[n - 1] = 1;

        RankSelectSpaceEfficient rs = new RankSelectSpaceEfficient(vector, 2);

        assertEquals(n - 1, rs.select(1));
        assertEquals(-1, rs.select(2));
    }

    @Test
    public void testSingleOneAtBeginning() {
        int n = 64;
        int[] vector = new int[n];
        vector[0] = 1;

        RankSelectSpaceEfficient rs = new RankSelectSpaceEfficient(vector, 2);

        assertEquals(0, rs.select(1));
        assertEquals(-1, rs.select(2));
    }

    @Test
    public void testRandomVectors() {
        Random rnd = new Random(1234);

        for (int t = 0; t < 20; t++) {
            int n = 128;
            int[] vector = new int[n];

            for (int i = 0; i < n; i++) {
                vector[i] = rnd.nextInt(3) == 0 ? 1 : 0; // ~1/3 ones
            }

            RankSelectSpaceEfficient rs = new RankSelectSpaceEfficient(vector, 2);
            List<Integer> ones = getPositions(vector);

            for (int r = 1; r <= ones.size(); r++) {
                int expected = ones.get(r - 1);
                int actual = rs.select(r);

                assertEquals(expected, actual, 
                    "select(" + r + ") mismatch in random vector");
            }

            assertEquals(-1, rs.select(ones.size() + 1));
        }
    }

    @Test
    public void testRankSelectConsistency() {
        int n = 256;
        int[] vector = new int[n];

        for (int i = 0; i < n; i++) {
            vector[i] = (i % 5 == 0 ? 1 : 0);
        }

        RankSelectSpaceEfficient rs = new RankSelectSpaceEfficient(vector, 2);

        int r = 0;
        for (int i = 0; i < n; i++) {
            if (vector[i] == 1) {
                r++;
                assertEquals(i, rs.select(r), 
                    "rank-select mismatch for r = " + r);
            }
        }
    }

}
