package rank_select;

public class RankSelectLookup implements RankSelectStrategy {
    int[] R;

    public RankSelectLookup(int[] vector) {
        R = precomputation(vector);
    }

    public int rank(int i) {
        return R[i];
    }

    public int select(int r) {
        int left = 0;
        int right = R.length - 1;
        int result = -1;
        if (r<=0) return -1;
        while (left <= right) {
            int mid = left + (right - left) / 2;

            if (R[mid] >= r) {
                result = mid;    // potential candidate
                right = mid - 1; // try to find an earlier one
            } else {
                left = mid + 1;
            }
        }

        return result; // either correct index or -1 if not found
    }

    private int[] precomputation(int[] v){
        int count = 0;
        int[] precomputedR = new int[v.length];
        for (int k=0; k < v.length ; k++){
            count += v[k];
            precomputedR[k] = count;
        }
        return precomputedR;
    }

}
