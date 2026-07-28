package rank_select;

import java.io.*;
import java.nio.file.*;
import java.util.*;

public class Main {
    private static final int WARMUP_QUERIES = 10_000;

    public static void main(String[] args) {
        // Check for --mode=construct flag
        String mode = "query";  // default
        int effectiveLength = args.length;
        if (args.length > 0 && args[args.length - 1].startsWith("--mode=")) {
            mode = args[args.length - 1].substring(7);
            effectiveLength = args.length - 1;
        }

        if (mode.equals("construct")) {
            runConstructMode(args, effectiveLength);
        } else {
            runQueryMode(args, effectiveLength);
        }
    }

    private static void runConstructMode(String[] args, int effectiveLength) {
        // Usage: java -jar app.jar <input_file> <impl> [k] --mode=construct
        if (effectiveLength < 2) {
            System.err.println("Usage: java -jar app.jar <input_file> <impl> [k] --mode=construct");
            System.err.println("  impl: Naive, Lookup, or SpaceEfficient");
            System.err.println("  k: (optional) parameter for SpaceEfficient, default 1");
            System.exit(1);
        }

        String inputFile = args[0];
        String implementation = args[1];
        int k = effectiveLength > 2 ? Integer.parseInt(args[2]) : 1;

        try {
            // Load bit vector (not timed - part of input)
            int[] vector = loadBitVector(inputFile);

            // Force GC before timing
            System.gc();

            // Time construction only
            long startTime = System.nanoTime();
            createStrategy(implementation, vector, k);
            long endTime = System.nanoTime();

            // Output construction time in nanoseconds
            System.out.println(endTime - startTime);

        } catch (Exception e) {
            System.err.println("Error: " + e.getMessage());
            e.printStackTrace();
            System.exit(1);
        }
    }

    private static void runQueryMode(String[] args, int effectiveLength) {
        if (effectiveLength < 4) {
            System.err.println("Usage: java -jar app.jar <input_file> <query_file> <impl> <query_type> [k]");
            System.err.println("  impl: Naive, Lookup, or SpaceEfficient");
            System.err.println("  query_type: rank or select");
            System.err.println("  k: (optional) parameter for SpaceEfficient, default 1");
            System.exit(1);
        }

        String inputFile = args[0];
        String queryFile = args[1];
        String implementation = args[2];
        String queryType = args[3];
        int k = effectiveLength > 4 ? Integer.parseInt(args[4]) : 1;

        try {
            // Load bit vector
            int[] vector = loadBitVector(inputFile);

            // Create implementation
            RankSelectStrategy strategy = createStrategy(implementation, vector, k);

            // Load queries
            int[] queries = loadQueries(queryFile);

            // Execute and time
            long totalTime = executeQueries(strategy, queries, queryType);

            // Output total time in nanoseconds
            System.out.println(totalTime);

        } catch (Exception e) {
            System.err.println("Error: " + e.getMessage());
            e.printStackTrace();
            System.exit(1);
        }
    }

    private static int[] loadBitVector(String path) throws IOException {
        List<String> lines = Files.readAllLines(Path.of(path));
        int n = Integer.parseInt(lines.get(0).trim());
        int[] vector = new int[n];
        for (int i = 0; i < n; i++) {
            vector[i] = Integer.parseInt(lines.get(i + 1).trim());
        }
        return vector;
    }

    private static int[] loadQueries(String path) throws IOException {
        List<String> lines = Files.readAllLines(Path.of(path));
        int count = Integer.parseInt(lines.get(0).trim());
        int[] queries = new int[count];
        for (int i = 0; i < count; i++) {
            queries[i] = Integer.parseInt(lines.get(i + 1).trim());
        }
        return queries;
    }

    private static RankSelectStrategy createStrategy(String impl, int[] vector, int k) {
        return switch (impl) {
            case "Naive" -> new RankSelectNaive(vector);
            case "Lookup" -> new RankSelectLookup(vector);
            case "SpaceEfficient" -> new RankSelectSpaceEfficient(vector, k);
            default -> throw new IllegalArgumentException("Unknown implementation: " + impl);
        };
    }

    private static long executeQueries(RankSelectStrategy strategy, int[] queries, String queryType) {
        // Warmup phase (discard timing)
        int warmupCount = Math.min(WARMUP_QUERIES, queries.length);
        if (queryType.equals("rank")) {
            for (int i = 0; i < warmupCount; i++) {
                strategy.rank(queries[i]);
            }
        } else {
            for (int i = 0; i < warmupCount; i++) {
                strategy.select(queries[i]);
            }
        }

        // Timed phase
        long startTime = System.nanoTime();

        if (queryType.equals("rank")) {
            for (int query : queries) {
                strategy.rank(query);
            }
        } else {
            for (int query : queries) {
                strategy.select(query);
            }
        }

        long endTime = System.nanoTime();
        return endTime - startTime;
    }
}
