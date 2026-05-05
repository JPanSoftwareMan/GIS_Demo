"""
***************************************************************************
*   By Justin Pan                                                                      *
*   QGIS Tech Export Demo Script
*   Description: This script is a simplified QGIS version of the tech export 
*   script that does near analysis, percent in EPZ, and assets on EPZ intersections. 
*   EPZ = Emergency planning zone
*   
***************************************************************************
"""

from typing import Any, Optional
from xml.dom import minidom
import pandas as pd
import os
from qgis.core import (
    QgsFeatureSink,
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingContext,
    QgsProcessingException,
    QgsProcessingFeedback,
    QgsProcessingParameterFeatureSink,
    QgsProcessingParameterFeatureSource,
    QgsVectorLayer,
    QgsLayerDefinition,
    QgsProject,
    QgsProcessingParameterCrs,
    QgsProcessingParameterString
)
from qgis import processing
import pandas

class TechExportGeneral(QgsProcessingAlgorithm):
    INPUT = "INPUT"
    OUTPUT = "OUTPUT"

    def name(self) -> str:
        return "myscript"

    def displayName(self) -> str:
        return "My Script"

    def group(self) -> str:
        return "Example scripts"

    def groupId(self) -> str:
        return "examplescripts"

    def shortHelpString(self) -> str:
        return "Example algorithm short description"

    def __init__(self):
        super().__init__()
        self.techExportLayer = r"C:\Users\genju\Documents\GIS\QGIS\BCExportFake.qlr"
        self.parkingLot = r"C:\Users\genju\Documents\GIS\QGIS\TechExportQGIS_Parking"
        self.techExportFolder = ""
        self.nearFeatures = ["firstnations"]
        self.percentFeatures = ["firstnations"]

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT,
                "EPZ layer",
                [QgsProcessing.SourceType.TypeVectorAnyGeometry],
            )
        )
        self.addParameter(QgsProcessingParameterFeatureSink(self.OUTPUT, "Output layer"))
        self.addParameter(
            QgsProcessingParameterCrs(
                "TARGET_CRS",
                "Target Coordinate System"
            )
        )
        self.addParameter(
            QgsProcessingParameterString(
                "EXPORT_FOLDER_NAME",
                "Export Folder Name",
                defaultValue=""
            )
        )
        #exportFolderPath = self.setupTechExportFolder(techExportFolderName, feedback)

    # Perform operations on the file here
    # ---------------------------------------------------------

    def setupTechExportFolder(self, techExportFolderName, feedback):
        full_path = os.path.join(self.parkingLot, techExportFolderName)

        if not os.path.exists(full_path):
            os.makedirs(full_path)
            feedback.pushInfo(f"Created export folder: {full_path}")
        else:
            feedback.pushInfo(f"Export folder already exists: {full_path}")

        return full_path

    # processAlgorithm now delegates the layer work to intersectLayers()
    # ---------------------------------------------------------
    def processAlgorithm(
        self,
        parameters,
        context: QgsProcessingContext,
        feedback: QgsProcessingFeedback,
    ) -> dict:

        epz_layer = self.parameterAsVectorLayer(parameters, self.INPUT, context)
        target_crs = self.parameterAsCrs(parameters, "TARGET_CRS", context)
        techExportFolderName = self.parameterAsFile(parameters, "EXPORT_FOLDER_NAME", context)
        self.techExportFolder = self.setupTechExportFolder(techExportFolderName, feedback)
        if epz_layer is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT))

        # Reproject EPZ layer if needed
        if epz_layer.crs() != target_crs:
            epz_layer = processing.run(
                "native:reprojectlayer",
                {
                    "INPUT": epz_layer,
                    "TARGET_CRS": target_crs,
                    "OUTPUT": "memory:",
                },
                context=context,
                feedback=feedback,
            )["OUTPUT"]

        # Run the new intersectLayers() method
        self.intersectLayers(epz_layer, target_crs, context, feedback)
        self.addTablestoExport(techExportFolderName,feedback)
        # Build final output sink (same as before)
        source = self.parameterAsSource(parameters, self.INPUT, context)
        sink, dest_id = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            source.fields(),
            source.wkbType(),
            source.sourceCrs(),
        )

        if sink is None:
            raise QgsProcessingException(self.invalidSinkError(parameters, self.OUTPUT))

        total = 100.0 / source.featureCount() if source.featureCount() else 0

        for current, feature in enumerate(source.getFeatures()):
            if feedback.isCanceled():
                break
            sink.addFeature(feature, QgsFeatureSink.FastInsert)
            feedback.setProgress(int(current * total))

        return {self.OUTPUT: dest_id}

    # ---------------------------------------------------------
    # Interesect all layers used in the tech export. Conduct near operations on layers if needed. 
    # ---------------------------------------------------------
    def intersectLayers(self, epz_layer, target_crs, context, feedback):

        feedback.pushInfo("Running intersectLayers()")

        loaded_layers = QgsLayerDefinition.loadLayerDefinitionLayers(self.techExportLayer)

        for layer in loaded_layers:
            csvOutput = os.path.join(self.techExportFolder, layer.name() + ".csv")
            nearOutput = os.path.join(self.techExportFolder, layer.name() + "_nearest.csv")
            overlayOutput = os.path.join(self.techExportFolder,layer.name() + "_percentinEPZ.csv")
            
            feedback.pushInfo("\nIntersecting with EPZ:")
            feedback.pushInfo(f"  Layer: {layer.name()}")
            feedback.pushInfo(f"  NearFeature list: {self.nearFeatures}")

            if layer.type() == QgsVectorLayer.VectorLayer:

                # --- Reproject if needed ---
                if layer.crs() != target_crs:
                    feedback.pushInfo("  Reprojecting layer...")
                    orig_name = layer.name()
                    layer = processing.run(
                        "native:reprojectlayer",
                        {
                            "INPUT": layer,
                            "TARGET_CRS": target_crs,
                            "OUTPUT": "memory:",
                        },
                        context=context,
                        feedback=feedback,
                    )["OUTPUT"]

                    layer.setName(orig_name)

                # --- Nearest feature analysis ---
                if layer.name() in self.nearFeatures:
                    feedback.pushInfo("  Running nearest feature analysis...")
                    processing.run(
                        "native:shortestline",
                        {
                            "SOURCE": layer,
                            "DESTINATION": epz_layer,
                            "METHOD": 0,
                            "NEIGHBORS": 1,
                            "DISTANCE": None,
                            "OUTPUT": nearOutput,
                        },
                        context=context,
                        feedback=feedback,
                        is_child_algorithm=True
                    )

                # --- Optional percent overlay (placeholder) ---
                if layer.name() in self.percentFeatures:
                    feedback.pushInfo("  Running percent overlay (placeholder)")
                    processing.run("native:calculatevectoroverlaps", 
                    {'INPUT':epz_layer,
                    'LAYERS':[layer],
                    'OUTPUT':overlayOutput,'GRID_SIZE':None})
                # processing.run(
                #     "native:joinattributesbylocation",
                #     {
                #         'INPUT': epz_layer,
                #         'JOIN': layer,
                #         'PREDICATE': [0],  # 0 = intersects
                #         'JOIN_FIELDS': [], # empty means keep all fields
                #         'METHOD': 0,       # take attributes of all matching features
                #         'DISCARD_NONMATCHING': False,
                #         'PREFIX': '',
                #         'OUTPUT': overlayOutput
                #     }
                # )
                # --- Intersect features ---
                feedback.pushInfo("  Extracting intersecting features...")
                processing.run(
                    "native:extractbylocation",
                    {
                        "INPUT": layer,
                        "PREDICATE": [0],
                        "INTERSECT": epz_layer,
                        "OUTPUT": csvOutput,
                    },
                    context=context,
                    feedback=feedback,
                    is_child_algorithm=True
                )
    def addTablestoExport(self, techExportFolderName,feedback):
        try:
            folder_path = os.path.join(self.parkingLot, techExportFolderName)

            output_excel = os.path.join(folder_path, f"{techExportFolderName}_Techexport.xlsx")

            combined_df_list = []

            for entry_name in os.listdir(folder_path):
                full_path = os.path.join(folder_path, entry_name)

                # Only process CSV files
                if os.path.isfile(full_path) and entry_name.lower().endswith(".csv"):
                    print(f"tech export csv found: {entry_name}")

                    df = pd.read_csv(full_path)

                    df.to_excel
            # Combine all tables
            final_df = pd.concat(combined_df_list, ignore_index=True)

            # Write to Excel
            final_df.to_excel(output_excel, sheet_name="All_CSVs", index=False)

            print(f"All CSVs written to one sheet: {output_excel}")
        except Exception as e:
            feedback.pushInfo("error in addTables to Export")
            feedback.pushInfo(str(e))
    def createInstance(self):
        return TechExportGeneral()

