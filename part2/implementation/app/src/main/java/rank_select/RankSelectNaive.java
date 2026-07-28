package rank_select;

public class RankSelectNaive implements RankSelectStrategy {
    private int[] vector;

    public RankSelectNaive(int[] vector) {
        this.vector = vector;
    }

    public int rank(int i) {
        int count = 0;
        for (int k=0; k <= i ; k++){
            count += vector[k];
        }
        return count;
    }

    public int select(int r) {
        int count = 0;
        int k;
        if (r<=0) return -1;
        for (k=0; k <vector.length ; k++){
            if (vector[k]==1){
                count++;
            }
            if(count == r){
                return k;
            }
        }
        return -1; //not found
    }
}
