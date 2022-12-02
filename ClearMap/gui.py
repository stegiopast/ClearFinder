import utils
import determine_path_rename_path_Tab
import resampling_alignment_Tab
import cell_detection_Tab 
import grouping_and_normalization_Tab 
import analysis_and_plots_Tab 


class Main_Window(utils.QWidget,
                  determine_path_rename_path_Tab.InitWorkspace,
                  determine_path_rename_path_Tab.RenameLayout,
                  resampling_alignment_Tab.ResamplingAlignment,
                  resampling_alignment_Tab.Resampling_Alignment_Layout,
                  cell_detection_Tab.CellDetection,
                  cell_detection_Tab.Cell_Detection_Layout,
                  grouping_and_normalization_Tab.Preanalysis_And_Normalization,
                  analysis_and_plots_Tab.Analysis_And_Plots_Layout,
                  ):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("ClearMap2 GUI")
        layout = utils.QVBoxLayout()
        self.setLayout(layout)
        tabs = utils.QTabWidget()
        self.my_working_directory = "not_selected"
        self.ws = None

        #Initialize Workspace, WorkingDirectory and Channel of Analysis
        tabs.addTab(self.rename_layout(), "Determine Path | Rename Path")
        tabs.addTab(self.resample_layout(), "Resampling | Alignment")
        tabs.addTab(self.cd_layout(), "Cell Detection")
        tabs.addTab(self.preanalysis_layout(), "Grouping and Normalization")
        tabs.addTab(self.analysis_layout(),"Analysis and Plots")
        layout.addWidget(tabs)


if __name__ == "__main__":
    app = utils.QApplication([])
    main_window = Main_Window()
    main_window.show()
    app.exec()
