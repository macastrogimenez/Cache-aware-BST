package rank_select;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;
import java.util.Arrays;

public class RankSelectSpaceEfficientTest {

    // Test bit packing
    @Test
    void testPackBits() {
        int[] vector = {
            1,0,1,1,0,0,0,1, 1,0,1,1,0,0,0,1,
            1,0,1,1,0,0,0,1, 1,0,1,1,0,0,0,1,
            1,0,1,1,0,0,0,1, 1,0,1,1,0,0,0,1,
            1,0,1,1,0,0,0,1, 1,0,1,1,0,0,0,1
        };

        int[] packed = RankSelectSpaceEfficient.packBits(vector);

        int expected = 0b10110001101100011011000110110001;

        assertEquals(expected, packed[0], "packed[0] mismatch");
        assertEquals(expected, packed[1], "packed[1] mismatch");
    }

    // Test precomputation
    @Test
    void testPrecomputation() {
        int[] vector = new int[64];
        Arrays.fill(vector, 0);
        vector[0] = 1;
        vector[31] = 1;
        vector[32] = 1;
        vector[63] = 1;

        int k = 1;
        RankSelectSpaceEfficient rs = new RankSelectSpaceEfficient(vector, k);

        int[] expectedRs = new int[64 / (32 * k) + 1];
        expectedRs[0] = (vector[0] == 1 ? 1 : 0);
        expectedRs[1] = Integer.bitCount(rs.packed[0]);
        expectedRs[2] = Integer.bitCount(rs.packed[0]) + Integer.bitCount(rs.packed[1]);

        assertArrayEquals(expectedRs, rs.Rs, "Precomputed Rs array mismatch");
    }

    // Test rank function
    @Test
    void testRankFunction() {
        int[] vector = {
            1,0,1,1,0,0,0,1, 1,0,1,1,0,0,0,1,
            1,0,1,1,0,0,0,1, 1,0,1,1,0,0,0,1,
            1,0,1,1,0,0,0,1, 1,0,1,1,0,0,0,1,
            1,0,1,1,0,0,0,1, 1,0,1,1,0,0,0,1
        };
        int k = 1;

        RankSelectSpaceEfficient rs = new RankSelectSpaceEfficient(vector, k);

        for (int i = 0; i < vector.length; i++) {
            int expected = 0;
            for (int j = 0; j <= i; j++) {
                expected += vector[j];
            }
            int got = rs.rank(i);

            assertEquals(expected, got, "rank(" + i + ") mismatch");
        }
    }
}
