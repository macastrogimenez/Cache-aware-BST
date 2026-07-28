/**
 * Some methods in this file were taken from the below source.
 * 
 * Source: https://algs4.cs.princeton.edu/32bst/BST.java.html
 * Credit: Robert Sedgewick, Kevin Wayne
 * License: GPLv3
 */


package skewed_binary_search_trees;
import java.util.List;
import java.util.NoSuchElementException;
import java.util.Optional;
// import java.util.HashSet;

import java.util.ArrayList;
import java.util.Collections;
import java.util.Set;


public class SearchTree implements SearchStrategy {
    private Node root;        
    double alpha;
    
    public Node getRoot(){
        return root;
    }// root of BST
    
    // searchTree constructor,
        // our implementation can exclusively built from a set
        // it does not support addition of single nodes
    public SearchTree(Set<Integer> ints, double alpha) {
        if (alpha <= 0.0 || alpha >= 1.0) {
            throw new IllegalArgumentException("Alpha must be between 0 and 1 (exclusive)");
        }
        
        this.alpha = alpha;
        
        // Build directly from sorted array
        ArrayList<Integer> sortedKeys = new ArrayList<>(ints);
        Collections.sort(sortedKeys);
        root = buildAlphaTree(sortedKeys, 0, sortedKeys.size() - 1);
    }


    public boolean isEmpty() {
        return size() == 0;
    }

    /**
     * Returns the number of key-value pairs in this symbol table.
     * @return the number of key-value pairs in this symbol table
     */
    public int size() {
        return size(root);
    }

    // return number of key-value pairs in BST rooted at x
    private int size(Node node) {
        if (node == null) return 0;
        else return node.getTreeSize();
    }
    
    // buildAlphaTree Helper for constructor: Build alpha-balanced tree from sorted array -> divide and conquer
        // just as in the sortedArray, we find the root first by using alpha, start and end
        // set the first node and recursively call buildAlphaTree on the remaining array left and right to the root
            // the key to build the skewed BST resides in using alpha to set the variable leftSize which we will use 
            // in the local variable rootIndex to keep creating right-leaning subtrees
            // start > end is the condition for finalization.
    private Node buildAlphaTree(List<Integer> keys, int start, int end) {
        // stop condition
        if (start > end) return null;
        
        int size = end - start + 1;
        int leftSize = (int) Math.floor(size * alpha);
        int rootIndex = start + leftSize;
        
        Node root = new Node(keys.get(rootIndex), size);
        root.setLeft(buildAlphaTree(keys, start, rootIndex - 1));
        root.setRight(buildAlphaTree(keys, rootIndex + 1, end));
        
        return root;
    }

    /**
     * Prints a visual representation of the tree structure
     */
    public void printTree() {
        printTree(root, "", true);
    }

    private void printTree(Node node, String prefix, boolean isTail) {
        if (node == null) {
            return;
        }
        
        // Print current node
        System.out.println(prefix + (isTail ? "└── " : "├── ") + node.getKey() + " (size: " + node.getTreeSize() + ")");
        
        // Prepare prefix for children
        String childPrefix = prefix + (isTail ? "    " : "│   ");
        
        // Print children (right first for better visualization)
        if (node.getLeft() != null || node.getRight() != null) {
            if (node.getRight() != null) {
                printTree(node.getRight(), childPrefix, node.getLeft() == null);
            } else {
                System.out.println(childPrefix + (node.getLeft() == null ? "└── " : "├── ") + "null");
            }
            
            if (node.getLeft() != null) {
                printTree(node.getLeft(), childPrefix, true);
            } else {
                System.out.println(childPrefix + "└── null");
            }
        }
    }

    /**
     * Returns the largest key in the symbol table less than or equal to {@code key}.
     *
     * @param  key the key
     * @return the largest key in the symbol table less than or equal to {@code key}
     * @throws NoSuchElementException if there is no such key
     * @throws IllegalArgumentException if {@code key} is {@code null}
     */

    /*
    
    private method called by pred() - it is a pseudo predHelper, the difference is the type being returned

    it checks for basic cases that would return exceptions, else calls the recursive method floor(Node node, Integer key)

    */
    private Integer floor(Integer key) {
        if (key == null) throw new IllegalArgumentException("argument to floor() is null");
        if (isEmpty()) throw new NoSuchElementException("calls floor() with empty symbol table");
        Node node = floor(root, key);
        if (node == null) throw new NoSuchElementException("argument to floor() is too small");
        else return node.getKey();
    }

    /*
    Helper function called by floor(Integer key)
     */

    private Node floor(Node node, Integer key) {
        // if the node passed is null return null
        if (node == null) return null;

        // set comparison between x and current node 
        int cmp = key.compareTo(node.getKey());

            // x and current node are equal -> return the node
        if (cmp == 0) return node;

            // x is smaller current node -> recurse on left child
        if (cmp <  0) return floor(node.getLeft(), key);

            // x is larger than current node -> recurse on right child
            // this also stores the largest 
        Node t = floor(node.getRight(), key);

        // after recursion on right side, right is not null return right
        if (t != null) return t;

        // if right is null then floor is the current node
        else return node;
    }

    // if x < min then return null
    // else call helper method floor()
    @Override
    public Optional<Integer> pred(int x) {

        if(x<min()){
            return Optional.ofNullable(null);    
        }
        else if (x>max()){return Optional.ofNullable(max());}
        else {
            Integer value = floor(x);
            return Optional.ofNullable(value);
        }
    }

    // Methods for finding min() value stored in the BST
    private Integer min() {
        if (isEmpty()) throw new NoSuchElementException("calls min() with empty symbol table");
        return min(root).getKey();
    }

    private Node min(Node node) {
        if (Optional.ofNullable(node.getLeft()).equals(Optional.empty())) return node;
        else                   return min(node.getLeft());
    }

        /**
     * Returns the largest key in the symbol table.
     *
     * @return the largest key in the symbol table
     * @throws NoSuchElementException if the symbol table is empty
     */
    public Integer max() {
        if (isEmpty()) throw new NoSuchElementException("calls max() with empty symbol table");
        return max(root).getKey();
    }

    private Node max(Node node) {
        if (node.getRight() == null) return node;
        else                    return max(node.getRight());
    }



    // public static void main(String[] args) {
    //     HashSet<Integer> set = new HashSet<Integer>();
    //     ;
        
    //     //set.add(1);
    //     set.add(2);
    //     set.add(3);
    //     set.add(5);
    //     //set.add(4); 
    //     set.add(8);
    //     set.add(11);
    //     set.add(13);


    //     SearchTree s = new SearchTree(set, 0.5);

    //     s.printTree();  // Visualize the tree

    //     System.out.println(s.pred(12)); // the result should be 11
    // }


}
