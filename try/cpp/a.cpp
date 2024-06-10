#include <cmath>
#include <list>
#include <map>


// the coordinate of chess
typedef std::pair<int, int> Coordinate;

// a valid operation
typedef std::pair<Coordinate, Coordinate> Operation;


// default Operation
const Operation OPERATION = { {-1, -1}, {-1, -1} };

// Node of the min-max searching tree
class Node {
public:
	float score;
	Operation operation;

	Node(float score, Operation operation = OPERATION) {
		this->score = score;
		this->operation = operation;
	}
};

// get an evaluate score of the board data
static float evaluate(int data[10][9], float score = 0) {
	for (int i = 0; i < 10; i++)
		for (int j = 0; j < 9; j++)
			score += data[i][j] < 0 ? -1 : 1;
	return score;
}

static Node alpha_beta_search(int data[10][9]) {
    Node node = Node(evaluate(data));

    return node;
}


// API for Python
extern "C" __attribute__((visibility("default"))) float search(int data[10][9], int result[4]) {
    Node node = alpha_beta_search(data);
    result[0] = node.operation.first.first;
    result[1] = node.operation.first.second;
    result[2] = node.operation.second.first;
    result[3] = node.operation.second.second;
    return node.score;
}

