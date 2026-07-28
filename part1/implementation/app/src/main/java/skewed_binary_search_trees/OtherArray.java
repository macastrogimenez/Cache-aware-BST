package skewed_binary_search_trees;
import java.util.*;

public class OtherArray implements SearchStrategy {
    double alpha;
    int[] vEBArray;
    int n;
    int currentIndex; // tracks next available index
    int topNodesBlockSize;
    Map<Node, Integer> nodeToIndex; // maps nodes to their array indices
    int minValue;
    int maxValue;

    public OtherArray(Set<Integer> ints, double alpha) {
        this.alpha = alpha;
        n = ints.size();
        topNodesBlockSize = (int) Math.ceil(Math.sqrt(n));
        vEBArray = new int[n * 3]; // each node needs 3 positions: [left_idx, value, right_idx]
        currentIndex = 0;
        nodeToIndex = new HashMap<>();
        minValue = Integer.MAX_VALUE;
        maxValue = Integer.MIN_VALUE;

        SearchTree s = new SearchTree(ints, alpha);
        Node root = s.getRoot(); // assuming you add a getter
        
        buildVEBLayout(root);
    }

    public void printArray(){
        StringBuilder s = new StringBuilder();
        for (int i : vEBArray) {
            s.append(i);
            s.append(" ,");
        }
        System.out.println(s.toString());
    }

    private void buildVEBLayout(Node root) {
        if (root == null) return;
        
        // Process top block first
        PriorityQueue<Node> topPQ = new PriorityQueue<>((n1, n2) -> 
            Integer.compare(n2.getTreeSize(), n1.getTreeSize()) // max-heap
        );
        
        // Collect top sqrt(n) nodes
        collectTopNodes(root, topPQ, topNodesBlockSize);
        
        // Insert top nodes and track their children
        Queue<Node> bottomNodes = new LinkedList<>();
        while (!topPQ.isEmpty()) {
            Node node = topPQ.poll();
            insertNode(node, bottomNodes);
        }
        
        // Recursively process bottom subtrees
        while (!bottomNodes.isEmpty()) {
            Node bottomRoot = bottomNodes.poll();
            if (bottomRoot != null) {
                buildVEBLayoutRecursive(bottomRoot);
            }
        }
        
        // After all nodes are inserted, update child pointers
        updateChildPointers();
    }


    private void insertNode(Node node, Queue<Node> bottomNodes) {
        // Skip if node already processed
        if (nodeToIndex.containsKey(node)) {
            return;
        }
        
        int nodeIndex = currentIndex;
        nodeToIndex.put(node, nodeIndex);
        
        // Reserve 3 positions: [left_idx, value, right_idx]
        int leftPtrIdx = currentIndex++;
        int valueIdx = currentIndex++;
        int rightPtrIdx = currentIndex++;
        
        // Store the value
        int nodeValue = node.getKey();
        vEBArray[valueIdx] = nodeValue;
        
        // Update min and max values
        minValue = Math.min(minValue, nodeValue);
        maxValue = Math.max(maxValue, nodeValue);
        
        // Store child indices (or -1 if null)
        Node left = node.getLeft();
        Node right = node.getRight();
        
        if (left != null) {
            // Check if left child already processed
            if (nodeToIndex.containsKey(left)) {
                // Point to the VALUE position of the child (starting index + 1)
                vEBArray[leftPtrIdx] = nodeToIndex.get(left) + 1;
            } else {
                // Will be filled when left is processed
                vEBArray[leftPtrIdx] = -1; // placeholder
                bottomNodes.add(left);
            }
        } else {
            vEBArray[leftPtrIdx] = -1;
        }
        
        if (right != null) {
            if (nodeToIndex.containsKey(right)) {
                // Point to the VALUE position of the child (starting index + 1)
                vEBArray[rightPtrIdx] = nodeToIndex.get(right) + 1;
            } else {
                vEBArray[rightPtrIdx] = -1; // placeholder
                bottomNodes.add(right);
            }
        } else {
            vEBArray[rightPtrIdx] = -1;
        }
    }
    
    //method to replace placeholders on vBEArray by actual indices
    private void updateChildPointers() {
        // After all nodes are inserted, update all placeholder -1s with actual indices
        for (Map.Entry<Node, Integer> entry : nodeToIndex.entrySet()) {
            Node node = entry.getKey();
            int nodeIdx = entry.getValue();
            
            int leftPtrIdx = nodeIdx;
            int rightPtrIdx = nodeIdx + 2;
            
            Node left = node.getLeft();
            Node right = node.getRight();
            
            if (left != null && nodeToIndex.containsKey(left)) {
                // Point to the VALUE position of the child (starting index + 1)
                vEBArray[leftPtrIdx] = nodeToIndex.get(left) + 1;
            }
            
            if (right != null && nodeToIndex.containsKey(right)) {
                // Point to the VALUE position of the child (starting index + 1)
                vEBArray[rightPtrIdx] = nodeToIndex.get(right) + 1;
            }
        }
    }

    private void buildVEBLayoutRecursive(Node root) {
        if (root == null) return;
        
        PriorityQueue<Node> pq = new PriorityQueue<>((n1, n2) -> 
            Integer.compare(n2.getTreeSize(), n1.getTreeSize())
        );
        
        int subtreeSize = root.getTreeSize();
        int blockSize = (int) Math.ceil(Math.sqrt(subtreeSize));
        
        collectTopNodes(root, pq, blockSize);
        
        Queue<Node> bottomNodes = new LinkedList<>();
        while (!pq.isEmpty()) {
            insertNode(pq.poll(), bottomNodes);
        }
        
        while (!bottomNodes.isEmpty()) {
            buildVEBLayoutRecursive(bottomNodes.poll());
        }
    }

    // Method to create temporary PQ on which to call the recursive method collectAllNodes() - to store all nodes and then only add
    // as many as the count (BlockSize) to the original PQ passed in the argument
    private void collectTopNodes(Node root, PriorityQueue<Node> pq, int count) {
        if (root == null || pq.size() >= count) return;
        
        // In-order traversal to collect nodes by size
        PriorityQueue<Node> temp = new PriorityQueue<>((n1, n2) -> 
            Integer.compare(n2.getTreeSize(), n1.getTreeSize())
        );
        
        collectAllNodes(root, temp);
        
        while (!temp.isEmpty() && pq.size() < count) {
            pq.add(temp.poll());
        }
    }

    // collects all nodes to a temporary PQ passed as argument so the top nodes can be retrieved in collectTopNodes()
    private void collectAllNodes(Node node, PriorityQueue<Node> pq) {
        if (node == null) return;
        pq.add(node);
        collectAllNodes(node.getLeft(), pq);
        collectAllNodes(node.getRight(), pq);
    }

    // recursive helper method to search for the predecessor of x in the BST, moving through it as per vBE array structure
    private Integer predHelper(int index, int x, Integer bestValue){
        int valueCurrentNode = vEBArray[index];
        if (valueCurrentNode == x){
            return valueCurrentNode;
        } else if (x < valueCurrentNode){ // if x less than value of the node go left
            int leftIndex = vEBArray[index-1]; 
            if (leftIndex != -1){ // if the child left is not null call predHelper recursively on 
                // Current node is too large, keep previous bestValue
                return predHelper(leftIndex, x, bestValue);
            }
        } else { // x > valueCurrentNode - go right
            // Current node is a valid candidate
            int rightIndex = vEBArray[index+1];
            if (rightIndex != -1){
                // Try to find something better in right subtree
                return predHelper(rightIndex, x, valueCurrentNode);
            } else {
                // Can't go right, current node is the best candidate
                return valueCurrentNode;
            }
        }
        return bestValue;
    }

    // pred method which checks for the basic cases where the output would be immediate and also calls recursive predHelper where necessary
    // returns optional to account for cases where there is no pred - such as an empty BST or x < min element in the BST.

    public Optional<Integer> pred(int x) {
        // if tree is empty or x is smaller than minimum value
        if (n == 0 || x < minValue){
            return Optional.ofNullable(null);
        }
        else if (x > maxValue){
            return Optional.ofNullable(maxValue);
        }
        else {
            Integer result = predHelper(1, x, null);
            return Optional.ofNullable(result);
        }
    }

    // Needed for base case x < min element in BST
    public int getMinValue() {
        return minValue;
    }

    // Needed for base case x > max element in BST -> no need to traverse the BST
    public int getMaxValue() {
        return maxValue;
    }

    

    // public static void main(String[] args) {
    //     HashSet<Integer> set = new HashSet<>();
    //     Random rand = new Random();
    //     while (set.size() < 40) {
    //         set.add(rand.nextInt(1000)); // random numbers 0-999
    //     }

    //     SearchTree s = new SearchTree(set, 0.3);
    //     OtherArray o = new OtherArray(set, 0.3);

    //     s.printTree();
    //     o.printArray();  

    //     //System.out.println(o.pred(12));
    // }
}
