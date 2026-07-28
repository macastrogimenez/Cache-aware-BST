package rank_select;

import java.util.Arrays;

public class RankSelectSpaceEfficient implements RankSelectStrategy {
    int[] packed;
    int[] Rs;
    final int k;
    
    public RankSelectSpaceEfficient(int[] vector, int k) {
        this.k = k;
        packed = packBits(vector);
        Rs = precomputation(packed, vector.length);
        //debugState(vector.length);

    }

    public int rank(int i) {
        if(i==0){
            return Rs[0];
        }
        
        int bigBlock = (i+1) / (32 * k);
        int offset   = (i+1) % (32 * k);

        int rank = Rs[bigBlock] ;
        if(bigBlock==0){
                rank-=Rs[0];
            }

        int start = bigBlock * k;          // starting int index
        int fullInts = offset / 32;
        int restBits = offset % 32;

        // Count full 32-bit ints
        for (int j = 0; j < fullInts; j++) {
            rank += Integer.bitCount(packed[start + j]);
        }

        // Count the remaining bits
        if (restBits > 0) {
            int block = packed[start + fullInts];
            int mask = -1 << (32 - restBits); // keep leftmost bits
            rank += Integer.bitCount(block & mask);
        }

        return rank;
    }

    public int select(int r) {
        if (r <= 0) return -1; // not defined for r<=0

        // Binary search the big block in Rs
        // Rs[b] = rank before block b
        // find the largest block where Rs[b] < r

        if(r==1 && Rs[0]==1){
            return 0;
        }

        int left = 0;
        int right = Rs.length - 1;

        while (left < right) {
            int mid = (left + right + 1) >>> 1;
            if (Rs[mid] < r) {
                left = mid;
            } else {
                right = mid - 1;
            }
        }

        int block = left;
        int baseRank = block==0? 0: Rs[block];           // rank before this big block - if the block was 0 then rank doesn't count, because 0 element is packed with others, and ranked separetely
        int remaining = r - baseRank;       // how many 1s inside this block to find

        // Linear scan inside the block
        // Each block has k packed integers
        int startInt = block * k;

        for (int j = 0; j < k; j++) {
            int idx = startInt + j;
            if (idx >= packed.length) return -1;

            int bits = packed[idx];
            int bitCount = Integer.bitCount(bits);

            if (remaining > bitCount) {
                remaining -= bitCount;
            } else {
                // the r-th 1 is inside this 32-bit word
                return findBitInWord(bits, remaining, idx);
            }
        }

        return -1; // not found
    }

    private int findBitInWord(int word, int remaining, int wordIndex) {
        // Scan from MSB (bit 31) to LSB (bit 0)
        for (int bit = 31; bit >= 0; bit--) {
            if (((word >>> bit) & 1) == 1) {
                remaining--;
                if (remaining == 0) {
                    int globalIndex = wordIndex * 32 + (31 - bit);
                    return globalIndex;
                }
            }
        }
        return -1;
    }



    public static int[] packBits(int[] vector){
        int n = vector.length;
        int[] packedBits = new int[n/32];

        for (int i=0; i<n; i++){
            if(vector[i]==1){
                int block = i/32;
                int offset = 31-(i%32);

                packedBits[block] |= (1<< offset);
            }
        }
        return packedBits;
    }

    public int[] precomputation(int[] packedBits, int vectorLength){
        int length = vectorLength/(32*k);
        int[] R = new int[length+1];
        int firstBit = (packed[0] >>> 31) & 1;
        R[0] = firstBit;
        int count = 0;
        int index =0;

        for(int i=1;i<length+1;i++){
            for (int j = 0; j<k; j++){
                count += Integer.bitCount(packed[index+j]);
            }
            R[i]  = count;
            index+=k;
        }

        return R;
    }

    private void debugState(int n) {
        System.out.println("Rs: " + Arrays.toString(Rs));
        System.out.println("packed length: " + packed.length);
        for (int i = 0; i < Math.min(packed.length, 8); i++) {
            System.out.printf("packed[%d]=%s\n", i, String.format("%32s", Integer.toBinaryString(packed[i])).replace(' ', '0'));
        }
        // total ones
        int tot = 0;
        for (int w : packed) tot += Integer.bitCount(w);
        System.out.println("totalOnes=" + tot + " n=" + n);
    }
}
