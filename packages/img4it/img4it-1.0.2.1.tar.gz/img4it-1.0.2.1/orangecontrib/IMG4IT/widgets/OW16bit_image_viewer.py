
from Orange.widgets.widget import OWWidget, Input
from AnyQt.QtWidgets import QApplication
import os
import Orange
import sys
# importe ton viewer sans le modifier
if "site-packages/Orange/widgets" in os.path.dirname(os.path.abspath(__file__)).replace("\\", "/"):
    from Orange.widgets.orangecontrib.IMG4IT.utils.tiff16_viewer import view_tiff_qt
else:
    from Orange.widgets.orangecontrib.IMG4IT.utils.tiff16_viewer import view_tiff_qt

class OWTiff16Viewer(OWWidget):
    name = "XRAY Viewer"
    description = "Show 16 bit image viewer"
    icon = "icons/viewer_xray_icon.png"
    if "site-packages/Orange/widgets" in os.path.dirname(os.path.abspath(__file__)).replace("\\", "/"):
        icon = "icons_dev/viewer_xray_icon.png"
    priority = 10
    want_control_area = False
    class Inputs:
        data = Input("Data", Orange.data.Table)


    def __init__(self):
        super().__init__()
        # Crée le viewer directement avec le chemin fixe
        self.viewer = None#view_tiff_qt(r"C:\Users\jean-\Desktop\pozipokaze\toto.tif", parent=self)
        # Insère le viewer dans la zone principale
        #self.mainArea.layout().addWidget(self.viewer)

    @Inputs.data
    def set_data(self, in_data):
        self.error("")
        if in_data is None:
            return

        self.data = in_data
        self.run()

    def run(self):
        if self.data is None:
            return


        # Verification of in_data
        self.error("")
        try:
            self.data.domain["image"]
        except KeyError:
            self.error('You need a "image" column in input data')
            return

        if type(self.data.domain["image"]).__name__ != 'StringVariable':
            self.error('"image" column needs to be a Text')
            return
        try:
            path_directory_of_image=str(self.data.domain["image"].attributes['origin'])
        except Exception as e:
            print(e)
            self.error('You need a "image" column from image analysis add on in input data')
            return

        liste_file=[]
        for element in self.data.get_column("image"):
            liste_file.append(path_directory_of_image+"/"+str(element))

        if len(liste_file)!=1:
            self.error('You need only one input images')
            return
        self.viewer =view_tiff_qt(liste_file[0], parent=self)
        layout = self.mainArea.layout()
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)

        layout.addWidget(self.viewer)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    my_widget = OWTiff16Viewer()
    my_widget.show()
    if hasattr(app, "exec"):
        app.exec()
    else:
        app.exec_()
    # from Orange.widgets.orangecontrib.IMG4IT.utils.tiff16_viewer import transform_tiff16_to_tiff8
    #
    # print("ici")
    # spec = "Transform | Min(I16) = 59221 | Max(I16) = 65535 | Mode = Sigmoide"
    # info = transform_tiff16_to_tiff8(r"C:\Users\jean-\Desktop\pozipokaze\toto.tif", r"C:\Users\jean-\Desktop\pozipokaze\toto_out.tif", spec)
    # print(info)