package skewed_binary_search_trees;

public class Node {
        private Integer key;           // sorted by key         // associated data
        private Node left, right;  // left and right subtrees
        private int treeSize;          // number of nodes in subtree

        public Node(Integer key, int size) {
            this.key = key;
            this.treeSize = size;
        }

        public Integer getKey() {
            return key;
        }

        public Node getLeft() {
            return left;
        }

        public Node getRight() {
            return right;
        }

        public int getTreeSize() {
            return treeSize;
        }

        public void setKey(Integer key){
            this.key = key;
        }

        public void setLeft(Node left) {
            this.left = left;
        }

        public void setRight(Node right) {
            this.right = right;
        }

        public void setTreeSize(int treeSize) {
            this.treeSize = treeSize;
        };
        
        

    }
