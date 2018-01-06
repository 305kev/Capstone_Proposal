from src.data_processing import load_data, DataProcessing
from sklearn.ensemble import RandomForestClassifier
import pickle


def build_model(input_file, output_model):
    """
    Build the model from training data and save as a pkl file.
    The current model being used is a ...

    :param input_file: Input jason file for raw data
    :param output_model: Output model in cPickle
    :return: Saved model to output_model
    """
    raw_data = load_data(input_file)
    pre_process_all = DataProcessing(True, raw_data)

    with open(output_model, 'wb') as f:
        pickle.dump( __ , f)


if __name__ == '__main__':
    """
    Debugging code for testing purposes
    """
    input_data = "data/data.json"
    output = "app/rf_test.pkl"
    build_model(input_data, output)

