
import utils
import determine_path_and_rename_filenames_tab
import preprocessing_tab
import cell_detection_assignment_tab
import train_network_tab
import grouping_and_normalization_tab
import analysis_and_plots_tab

def on_top_clicked():
    alert = utils.QMessageBox()
    alert.setText("You moved to the top !")
    alert.exec()


class MainWindow(utils.QWidget,
                  determine_path_and_rename_filenames_tab.InitWorkspace,
                  determine_path_and_rename_filenames_tab.RenameLayout,
                  preprocessing_tab.Preprocessing,
                  preprocessing_tab.PreprocessingLayout,
                  cell_detection_assignment_tab.CellDetection,
                  cell_detection_assignment_tab.CellDetectionLayout,
                  train_network_tab.TrainNetwork,
                  train_network_tab.TrainingNetworkLayout,
                  analysis_and_plots_tab.AnalysisAndPlots,
                  grouping_and_normalization_tab.GroupingAndNormalization
                  ):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cellfinder GUI")
        self.resize(1600,800)
        layout = utils.QVBoxLayout()
        self.setLayout(layout)
        tabs = utils.QTabWidget()
        tabs.addTab(self.rename_layout(), "Determine Path and Rename Filenames")
        tabs.addTab(self.preprocess_layout(), "Preprocessing")
        tabs.addTab(self.cd_layout(), "Cell Detection | Assignment")
        tabs.addTab(self.training_layout(), "Train Network")  
        tabs.addTab(self.preanalysis_layout(), "Grouping and Normalization")
        tabs.addTab(self.analysis_layout(), "Analysis and Plots")
        layout.addWidget(tabs)
        self.my_working_directory = ""
        self.channel_chosen = ""
        
    def warning_ws(self):
        alert = utils.QMessageBox()
        alert.setText("You didn't choose a sample yet! Please choose a sample.")
        alert.exec()

if __name__ == "__main__":
    app = utils.QApplication([])
    MainWindow = MainWindow()
    MainWindow.show()
    app.exec()
