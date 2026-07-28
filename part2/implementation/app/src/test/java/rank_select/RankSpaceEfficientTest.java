package rank_select;

import org.junit.jupiter.api.Test;
import java.util.Arrays;
import java.util.Random;

import static org.junit.jupiter.api.Assertions.assertEquals;

public class RankSpaceEfficientTest {

    // All zeros
    @Test
    public void testAllZeros() {
        int n = 64;
        int[] vector = new int[n];
        Arrays.fill(vector, 0);

        RankSelectSpaceEfficient rs = new RankSelectSpaceEfficient(vector, 2);

        for (int i = 0; i < n; i++) {
            assertEquals(0, rs.rank(i), "Failed at index " + i);
        }
    }

    //  All ones
    @Test
    public void testAllOnes() {
        int n = 64;
        int[] vector = new int[n];
        Arrays.fill(vector, 1);

        RankSelectSpaceEfficient rs = new RankSelectSpaceEfficient(vector, 2);

        for (int i = 0; i < n; i++) {
            assertEquals(i + 1, rs.rank(i), "Failed at index " + i);
        }
    }

    // Alternating ones and zeros
    @Test
    public void testAlternatingBits() {
        int n = 64;
        int[] vector = new int[n];
        for (int i = 0; i < n; i++) vector[i] = i % 2;

        RankSelectSpaceEfficient rs = new RankSelectSpaceEfficient(vector, 2);

        int count = 0;
        for (int i = 0; i < n; i++) {
            if (vector[i] == 1) count++;
            assertEquals(count, rs.rank(i), "Failed at index " + i);
        }
    }

    // Sparse ones 
    @Test
    public void testSparseOnes() {
        int n = 64;
        int[] vector = new int[n];
        vector[0] = 1;
        vector[15] = 1;
        vector[31] = 1;
        vector[32] = 1;
        vector[63] = 1;

        RankSelectSpaceEfficient rs = new RankSelectSpaceEfficient(vector, 2);

        int count = 0;
        for (int i = 0; i < n; i++) {
            if (vector[i] == 1) count++;
            assertEquals(count, rs.rank(i), "Failed at index " + i);
        }
    }

    // Random vector
    @Test
    public void testRandomVector() {
        int n = 128;
        int[] vector = new int[n];
        Random rand = new Random(42);
        for (int i = 0; i < n; i++) vector[i] = rand.nextBoolean() ? 1 : 0;

        RankSelectSpaceEfficient rs = new RankSelectSpaceEfficient(vector, 4);

        int count = 0;
        for (int i = 0; i < n; i++) {
            if (vector[i] == 1) count++;
            assertEquals(count, rs.rank(i), "Failed at index " + i);
        }
    }
}
