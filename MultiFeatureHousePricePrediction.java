import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.util.*;

public class MultiFeatureHousePricePrediction {

    public static void main(String[] args) {
        ArrayList<double[]> features = new ArrayList<>();
        ArrayList<Double> targets = new ArrayList<>();

        try (BufferedReader br = new BufferedReader(new FileReader("data.csv"))) {
            String line;
            boolean isFirstLine = true;

            while ((line = br.readLine()) != null) {
                if (isFirstLine) {
                    isFirstLine = false;
                    continue;
                }

                String[] values = line.split(",");
                double area = Double.parseDouble(values[0]);
                double bedrooms = Double.parseDouble(values[1]);
                double age = Double.parseDouble(values[2]);
                double price = Double.parseDouble(values[3]);

                features.add(new double[]{area, bedrooms, age});
                targets.add(price);
            }
        } catch (IOException e) {
            System.out.println("Error reading CSV: " + e.getMessage());
            return;
        }

        int m = features.size(); // Number of samples
        int n = 3; // Number of features

        double[][] X = new double[m][n + 1]; // Add bias term (1)
        double[] Y = new double[m];

        for (int i = 0; i < m; i++) {
            X[i][0] = 1; // Bias
            for (int j = 0; j < n; j++) {
                X[i][j + 1] = features.get(i)[j];
            }
            Y[i] = targets.get(i);
        }

        double[] theta = normalEquation(X, Y);

        Scanner scanner = new Scanner(System.in);
        System.out.println("Enter house details:");
        System.out.print("Area (sq ft): ");
        double area = scanner.nextDouble();
        System.out.print("Bedrooms: ");
        double bedrooms = scanner.nextDouble();
        System.out.print("Age (years): ");
        double age = scanner.nextDouble();
        scanner.close();

        double prediction = theta[0] + theta[1] * area + theta[2] * bedrooms + theta[3] * age;
        System.out.printf("Predicted price: $%.2f\n", prediction);
    }

    // Normal Equation for linear regression: θ = (XᵀX)⁻¹ Xᵀy
    public static double[] normalEquation(double[][] X, double[] y) {
        int m = X.length;
        int n = X[0].length;

        double[][] XT = transpose(X);
        double[][] XTX = multiplyMatrices(XT, X);
        double[][] XTXInv = invertMatrix(XTX);
        double[][] XTY = multiplyMatrixVector(XT, y);
        double[] theta = multiplyMatrixVector(XTXInv, XTY);

        return theta;
    }

    public static double[][] transpose(double[][] matrix) {
        int r = matrix.length;
        int c = matrix[0].length;
        double[][] result = new double[c][r];

        for (int i = 0; i < r; i++)
            for (int j = 0; j < c; j++)
                result[j][i] = matrix[i][j];
        return result;
    }

    public static double[][] multiplyMatrices(double[][] A, double[][] B) {
        int r1 = A.length, c1 = A[0].length, c2 = B[0].length;
        double[][] result = new double[r1][c2];

        for (int i = 0; i < r1; i++) {
            for (int j = 0; j < c2; j++) {
                for (int k = 0; k < c1; k++) {
                    result[i][j] += A[i][k] * B[k][j];
                }
            }
        }
        return result;
    }

    public static double[][] multiplyMatrixVector(double[][] A, double[] x) {
        int rows = A.length;
        int cols = A[0].length;
        double[][] result = new double[rows][1];

        for (int i = 0; i < rows; i++) {
            for (int j = 0; j < cols; j++) {
                result[i][0] += A[i][j] * x[j];
            }
        }
        return result;
    }

    public static double[] multiplyMatrixVector(double[][] A, double[][] B) {
        int rows = A.length;
        double[] result = new double[rows];

        for (int i = 0; i < rows; i++) {
            result[i] = B[i][0];
        }
        return result;
    }

    public static double[][] invertMatrix(double[][] A) {
        int n = A.length;
        double[][] inv = new double[n][n];
        double[][] aug = new double[n][2 * n];

        // Create augmented matrix [A | I]
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                aug[i][j] = A[i][j];
                aug[i][j + n] = (i == j) ? 1 : 0;
            }
        }

        // Gauss-Jordan elimination
        for (int i = 0; i < n; i++) {
            double pivot = aug[i][i];
            if (pivot == 0) throw new ArithmeticException("Matrix is singular.");

            for (int j = 0; j < 2 * n; j++) {
                aug[i][j] /= pivot;
            }

            for (int k = 0; k < n; k++) {
                if (k != i) {
                    double factor = aug[k][i];
                    for (int j = 0; j < 2 * n; j++) {
                        aug[k][j] -= factor * aug[i][j];
                    }
                }
            }
        }

        // Extract inverse matrix
        for (int i = 0; i < n; i++)
            System.arraycopy(aug[i], n, inv[i], 0, n);

        return inv;
    }
}
