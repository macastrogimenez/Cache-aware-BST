package rank_select;

import static org.junit.jupiter.api.Assertions.*;
import org.junit.jupiter.api.Test;

import java.io.IOException;
import java.nio.file.*;
import java.util.*;

public class RankSelectAutomatedTest {

    /** Converts "010011" → int[]{0,1,0,0,1,1} */
    private int[] toIntArray(String bits) {
        int[] v = new int[bits.length()];
        for (int i = 0; i < bits.length(); i++) {
            v[i] = (bits.charAt(i) == '1') ? 1 : 0;
        }
        return v;
    }

    @Test
    void testAllImplementations() throws IOException {
        Path dir = Paths.get("test_inputs");

        try (DirectoryStream<Path> stream = Files.newDirectoryStream(dir, "*.txt")) {
            for (Path file : stream) {
                runCase(file);
            }
        }
    }

    private void runCase(Path file) throws IOException {
        List<String> lines = Files.readAllLines(file);
        int idx = 0;

        // Read N
        int n = Integer.parseInt(lines.get(idx++).trim());

        // Read bitstring
        String bitString = lines.get(idx++).trim();
        assertEquals(n, bitString.length(), "Bitstring length mismatch in: " + file);

        int[] vector = toIntArray(bitString);

        // Instantiate ORACLE
        RankSelectNaive oracle = new RankSelectNaive(vector);

        // Instantiate IMPLEMENTATIONS
        RankSelectLookup lookup = new RankSelectLookup(vector);
        RankSelectSpaceEfficient spaceEff = new RankSelectSpaceEfficient(vector, 2);

        System.out.println("Testing: " + file);

        //  RANK tests 
        int numRank = Integer.parseInt(lines.get(idx++).trim());
        for (int t = 0; t < numRank; t++) {
            String[] parts = lines.get(idx++).split(" ");
            int i = Integer.parseInt(parts[1]);

            int expected = oracle.rank(i);

            assertEquals(expected, lookup.rank(i), 
                file + " : lookup.rank(" + i + ") mismatch");
            assertEquals(expected, spaceEff.rank(i),
                file + " : spaceEff.rank(" + i + ") mismatch");
        }

        //  SELECT tests 
        int numSelect = Integer.parseInt(lines.get(idx++).trim());
        for (int t = 0; t < numSelect; t++) {
            String[] parts = lines.get(idx++).split(" ");
            int r = Integer.parseInt(parts[1]);

            int expected = oracle.select(r);

            assertEquals(expected, lookup.select(r),
                file + " : lookup.select(" + r + ") mismatch");

            assertEquals(expected, spaceEff.select(r),
                file + " : spaceEff.select(" + r + ") mismatch");
        }
    }
}

