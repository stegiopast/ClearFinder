import utils
import DeterminePath_RenamePath_Tab
import Resampling_Alignment_Tab
import Cell_Detection_Tab
import Grouping_and_Normalization_Tab
import Analysis_and_Plots_Tab


class Main_Window(utils.QWidget,
                  DeterminePath_RenamePath_Tab._init_Workspace,
                  DeterminePath_RenamePath_Tab._rename_Layout,
                  Resampling_Alignment_Tab.Resampling_Alignment,
                  Resampling_Alignment_Tab.Resampling_Alignment_Layout,
                  Cell_Detection_Tab.Cell_Detection,
                  Cell_Detection_Tab.Cell_Detection_Layout,
                  Grouping_and_Normalization_Tab._Preanalysis_and_Normalization,
                  Analysis_and_Plots_Tab._Analysis_and_Plots_Layout,
                  ):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("ClearMap2 GUI")
        layout = utils.QVBoxLayout()
        self.setLayout(layout)
        tabs = utils.QTabWidget()
        #Initialize Workspace, WorkingDirectory and Channel of Analysis
        tabs.addTab(self.rename_layout(), "Determine Path | Rename Path")
        tabs.addTab(self.resample_layout(), "Resampling | Alignment")
        tabs.addTab(self.cd_layout(), "Cell Detection")
        tabs.addTab(self.preanalysis_layout(), "Grouping and Normalization")
        tabs.addTab(self.analysis_layout(),"Analysis and Plots")
        layout.addWidget(tabs)
        #self.debug = False


if __name__ == "__main__":
    app = utils.QApplication([])
    main_window = Main_Window()
    main_window.show()
    app.exec()
