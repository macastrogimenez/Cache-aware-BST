package skewed_binary_search_trees;

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

public class Main {
    public static void main(String[] args) {
        ParsedData data = readData(args);

        // Build the data structure (not timed)
        SearchStrategy s = createStructure(data.searchStrategy, data.ints, data.alpha);

        // Process queries and output timings
        for (int query : data.queries) {
            long startTime = System.nanoTime();
            s.pred(query);
            long endTime = System.nanoTime();
            
            long elapsedNanos = endTime - startTime;
            System.out.println(elapsedNanos);
        }
    }

    private static SearchStrategy createStructure(String strategy, Set<Integer> ints, double alpha) {
        return switch (strategy) {
            case "SortedArray" -> new SortedArray(ints, alpha);
            case "SearchTree" -> new SearchTree(ints, alpha);
            case "OtherArray" -> new OtherArray(ints, alpha);
            default -> throw new IllegalArgumentException("Unknown strategy: " + strategy);
        };
    }

    private static ParsedData readData(String[] args) {
        // Expect input in format: FILE_PATH SEARCH_STRATEGY ALPHA
        // File format:
        // {number of integers} {number of queries}
        // {lines of integers}
        // {lines of queries}

        if (args.length != 1) {
            System.out.println("Expected to receive args of length 1. Instead got: " + args.length + " strings.");

            for (var arg : args) {
                System.out.println(arg);
            }

            System.exit(1);
        }


        String[] tokens = args[0].split(" ");


        String filePath = tokens[0];
        String searchStrategy = tokens[1];
        double alpha = Double.parseDouble(tokens[2]);

        // Read file
        Set<Integer> ints = new HashSet<>();
        List<Integer> queries = new ArrayList<>();

        try (BufferedReader reader = new BufferedReader(new FileReader(filePath))) {
            // Read first line: {number of integers} {number of queries}
            String firstLine = reader.readLine();
            if (firstLine == null) {
                throw new IOException("Empty file");
            }
            
            String[] parts = firstLine.trim().split(" ");
            if (parts.length != 2) {
                throw new IOException("First line must contain two parts: {number of integers} {number of queries}");
            }
            
            int numInts = Integer.parseInt(parts[0]);
            int numQueries = Integer.parseInt(parts[1]);

            // Validate search strategy
            List<String> validStrategies = Arrays.asList("SortedArray", "SearchTree", "OtherArray");
            if (!validStrategies.contains(searchStrategy)) {
                throw new IOException("Invalid search strategy: " + searchStrategy + 
                    ". Allowed strategies: SortedArray, SearchTree, OtherArray");
            }

            // Read integers
            for (int i = 0; i < numInts; i++) {
                String line = reader.readLine();
                if (line == null) {
                    throw new IOException("Unexpected end of file while reading integers");
                }
                ints.add(Integer.parseInt(line.trim()));
            }

            // Read queries
            for (int i = 0; i < numQueries; i++) {
                String line = reader.readLine();
                if (line == null) {
                    throw new IOException("Unexpected end of file while reading queries");
                }
                queries.add(Integer.parseInt(line.trim()));
            }

        } catch (IOException | NumberFormatException e) {
            System.err.println("Error reading file: " + e.getMessage());
            e.printStackTrace();
            System.exit(1);
        }

        return new ParsedData(searchStrategy, ints, alpha, queries);
    }

    private record ParsedData(String searchStrategy, Set<Integer> ints, double alpha, List<Integer> queries) {}
}

