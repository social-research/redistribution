// Fixed treatment parameters
export const numRounds = 3
export const durRound = 300  // 300 seconds - UPDATE TO 30 seconds!!!
export const conversionRate = 0.02

// High and low wealth
// We will assume 15 poor, 9 rich
export const richscore = 200
export const poorscore = 20

// Observation networks

export const two_net = {
  0: [1],
  1: [0],
}

export const four_net = {
  0: [1, 2],
  1: [2, 3],
  2: [3, 0],
  3: [0, 1],
}

export const nine_net = {
  0: [1, 2, 3, 4, 5, 6, 7, 8],
  1: [2, 3, 4, 5, 6, 7, 8, 0],
  2: [3, 4, 5, 6, 7, 8, 0, 1],
  3: [4, 5, 6, 7, 8, 0, 1, 2],
  4: [5, 6, 7, 8, 0, 1, 2, 3],
  5: [6, 7, 8, 0, 1, 2, 3, 4],
  6: [7, 8, 0, 1, 2, 3, 4, 5],
  7: [8, 0, 1, 2, 3, 4, 5, 6],
  8: [0, 1, 2, 3, 4, 5, 6, 7],
}

export const homophil_net = {
  0: [1, 2, 3, 4, 6, 8, 10, 12],
  1: [2, 3, 4, 5, 7, 9, 11, 13],
  2: [3, 4, 5, 6, 8, 10, 12, 14],
  3: [4, 5, 6, 7, 9, 11, 13, 15],
  4: [5, 6, 7, 8, 10, 12, 14, 16],
  5: [6, 7, 8, 9, 11, 13, 15, 17],
  6: [7, 8, 9, 10, 12, 14, 16, 18],
  7: [8, 9, 10, 11, 13, 15, 17, 19],
  8: [9, 10, 11, 12, 14, 16, 18, 20],
  9: [10, 11, 12, 13, 15, 17, 19, 21],
  10: [11, 12, 13, 14, 16, 18, 20, 22],
  11: [12, 13, 14, 15, 17, 19, 21, 23],
  12: [13, 14, 15, 16, 18, 20, 22, 0],
  13: [14, 15, 16, 17, 19, 21, 23, 1],
  14: [15, 16, 17, 18, 20, 22, 0, 2],
  15: [16, 17, 18, 19, 21, 23, 1, 3],
  16: [17, 18, 19, 20, 22, 0, 2, 4],
  17: [18, 19, 20, 21, 23, 1, 3, 5],
  18: [19, 20, 21, 22, 0, 2, 4, 6],
  19: [20, 21, 22, 23, 1, 3, 5, 7],
  20: [21, 22, 23, 0, 2, 4, 6, 8],
  21: [22, 23, 0, 1, 3, 5, 7, 9],
  22: [23, 0, 1, 2, 4, 6, 8, 10],
  23: [0, 1, 2, 3, 5, 7, 9, 11],
};

export const heterophil_net = {
  0: [1, 2, 3, 5, 7, 9, 11, 13],
  1: [2, 3, 4, 6, 8, 10, 12, 14],
  2: [3, 4, 5, 7, 9, 11, 13, 15],
  3: [4, 5, 6, 8, 10, 12, 14, 16],
  4: [5, 6, 7, 9, 11, 13, 15, 17],
  5: [6, 7, 8, 10, 12, 14, 16, 18],
  6: [7, 8, 9, 11, 13, 15, 17, 19],
  7: [8, 9, 10, 12, 14, 16, 18, 20],
  8: [9, 10, 11, 13, 15, 17, 19, 21],
  9: [10, 11, 12, 14, 16, 18, 20, 22],
  10: [11, 12, 13, 15, 17, 19, 21, 23],
  11: [12, 13, 14, 16, 18, 20, 22, 0],
  12: [13, 14, 15, 17, 19, 21, 23, 1],
  13: [14, 15, 16, 18, 20, 22, 0, 2],
  14: [15, 16, 17, 19, 21, 23, 1, 3],
  15: [16, 17, 18, 20, 22, 0, 2, 4],
  16: [17, 18, 19, 21, 23, 1, 3, 5],
  17: [18, 19, 20, 22, 0, 2, 4, 6],
  18: [19, 20, 21, 23, 1, 3, 5, 7],
  19: [20, 21, 22, 0, 2, 4, 6, 8],
  20: [21, 22, 23, 1, 3, 5, 7, 9],
  21: [22, 23, 0, 2, 4, 6, 8, 10],
  22: [23, 0, 1, 3, 5, 7, 9, 11],
  23: [0, 1, 2, 4, 6, 8, 10, 12],
};

export const richvis_net = {
  0: [1, 2, 3, 5, 7, 9, 11, 13],
  1: [2, 3, 4, 5, 7, 9, 11, 13],
  2: [3, 4, 5, 7, 9, 11, 13, 15],
  3: [4, 5, 6, 7, 9, 11, 13, 15],
  4: [5, 6, 7, 9, 11, 13, 15, 17],
  5: [6, 7, 8, 9, 11, 13, 15, 17],
  6: [7, 8, 9, 11, 13, 15, 17, 19],
  7: [8, 9, 10, 11, 13, 15, 17, 19],
  8: [9, 10, 11, 13, 15, 17, 19, 21],
  9: [10, 11, 12, 13, 15, 17, 19, 21],
  10: [11, 12, 13, 15, 17, 19, 21, 23],
  11: [12, 13, 14, 15, 17, 19, 21, 23],
  12: [13, 14, 15, 17, 19, 21, 23, 1],
  13: [14, 15, 16, 17, 19, 21, 23, 1],
  14: [15, 16, 17, 19, 21, 23, 1, 3],
  15: [16, 17, 18, 19, 21, 23, 1, 3],
  16: [17, 18, 19, 21, 23, 1, 3, 5],
  17: [18, 19, 20, 21, 23, 1, 3, 5],
  18: [19, 20, 21, 23, 1, 3, 5, 7],
  19: [20, 21, 22, 23, 1, 3, 5, 7],
  20: [21, 22, 23, 1, 3, 5, 7, 9],
  21: [22, 23, 0, 1, 3, 5, 7, 9],
  22: [23, 0, 1, 3, 5, 7, 9, 11],
  23: [0, 1, 2, 3, 5, 7, 9, 11],
};

export const poorvis_net = {
  0: [1, 2, 3, 4, 6, 8, 10, 12],
  1: [2, 3, 4, 6, 8, 10, 12, 14],
  2: [3, 4, 5, 6, 8, 10, 12, 14],
  3: [4, 5, 6, 8, 10, 12, 14, 16],
  4: [5, 6, 7, 8, 10, 12, 14, 16],
  5: [6, 7, 8, 10, 12, 14, 16, 18],
  6: [7, 8, 9, 10, 12, 14, 16, 18],
  7: [8, 9, 10, 12, 14, 16, 18, 20],
  8: [9, 10, 11, 12, 14, 16, 18, 20],
  9: [10, 11, 12, 14, 16, 18, 20, 22],
  10: [11, 12, 13, 14, 16, 18, 20, 22],
  11: [12, 13, 14, 16, 18, 20, 22, 0],
  12: [13, 14, 15, 16, 18, 20, 22, 0],
  13: [14, 15, 16, 18, 20, 22, 0, 2],
  14: [15, 16, 17, 18, 20, 22, 0, 2],
  15: [16, 17, 18, 20, 22, 0, 2, 4],
  16: [17, 18, 19, 20, 22, 0, 2, 4],
  17: [18, 19, 20, 22, 0, 2, 4, 6],
  18: [19, 20, 21, 22, 0, 2, 4, 6],
  19: [20, 21, 22, 0, 2, 4, 6, 8],
  20: [21, 22, 23, 0, 2, 4, 6, 8],
  21: [22, 23, 0, 2, 4, 6, 8, 10],
  22: [23, 0, 1, 2, 4, 6, 8, 10],
  23: [0, 1, 2, 4, 6, 8, 10, 12],
};

export const segregated_net = {
  0: [2, 4, 6, 8, 10, 12, 14, 16],
  1: [3, 5, 7, 9, 11, 13, 15, 17],
  2: [4, 6, 8, 10, 12, 14, 16, 18],
  3: [5, 7, 9, 11, 13, 15, 17, 19],
  4: [6, 8, 10, 12, 14, 16, 18, 20],
  5: [7, 9, 11, 13, 15, 17, 19, 21],
  6: [8, 10, 12, 14, 16, 18, 20, 22],
  7: [9, 11, 13, 15, 17, 19, 21, 23],
  8: [10, 12, 14, 16, 18, 20, 22, 0],
  9: [11, 13, 15, 17, 19, 21, 23, 1],
  10: [12, 14, 16, 18, 20, 22, 0, 2],
  11: [13, 15, 17, 19, 21, 23, 1, 3],
  12: [14, 16, 18, 20, 22, 0, 2, 4],
  13: [15, 17, 19, 21, 23, 1, 3, 5],
  14: [16, 18, 20, 22, 0, 2, 4, 6],
  15: [17, 19, 21, 23, 1, 3, 5, 7],
  16: [18, 20, 22, 0, 2, 4, 6, 8],
  17: [19, 21, 23, 1, 3, 5, 7, 9],
  18: [20, 22, 0, 2, 4, 6, 8, 10],
  19: [21, 23, 1, 3, 5, 7, 9, 11],
  20: [22, 0, 2, 4, 6, 8, 10, 12],
  21: [23, 1, 3, 5, 7, 9, 11, 13],
  22: [0, 2, 4, 6, 8, 10, 12, 14],
  23: [1, 3, 5, 7, 9, 11, 13, 15],
};

export const representative_net = {
  0: [1, 2, 3, 4, 5, 6, 7, 8],
  1: [2, 3, 4, 5, 6, 7, 8, 9],
  2: [3, 4, 5, 6, 7, 8, 9, 10],
  3: [4, 5, 6, 7, 8, 9, 10, 11],
  4: [5, 6, 7, 8, 9, 10, 11, 12],
  5: [6, 7, 8, 9, 10, 11, 12, 13],
  6: [7, 8, 9, 10, 11, 12, 13, 14],
  7: [8, 9, 10, 11, 12, 13, 14, 15],
  8: [9, 10, 11, 12, 13, 14, 15, 16],
  9: [10, 11, 12, 13, 14, 15, 16, 17],
  10: [11, 12, 13, 14, 15, 16, 17, 18],
  11: [12, 13, 14, 15, 16, 17, 18, 19],
  12: [13, 14, 15, 16, 17, 18, 19, 20],
  13: [14, 15, 16, 17, 18, 19, 20, 21],
  14: [15, 16, 17, 18, 19, 20, 21, 22],
  15: [16, 17, 18, 19, 20, 21, 22, 23],
  16: [17, 18, 19, 20, 21, 22, 23, 0],
  17: [18, 19, 20, 21, 22, 23, 0, 1],
  18: [19, 20, 21, 22, 23, 0, 1, 2],
  19: [20, 21, 22, 23, 0, 1, 2, 3],
  20: [21, 22, 23, 0, 1, 2, 3, 4],
  21: [22, 23, 0, 1, 2, 3, 4, 5],
  22: [23, 0, 1, 2, 3, 4, 5, 6],
  23: [0, 1, 2, 3, 4, 5, 6, 7],
};

