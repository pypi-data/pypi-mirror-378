from dataclasses import dataclass
import json


@dataclass
class Project:
    """
    This dataclass extract the information retrieved from the getProjet method.
    It flatten the elements and gives you insights on what your project contains.
    """

    def __init__(self, projectDict: dict = None, dvIdSuffix: bool = False):
        """
        Instancialize the class.
        Arguments:
            projectDict : REQUIRED : the dictionary of the project (returned by getProject method)
            dvIdSuffix : OPTIONAL : If you want to have the data view ID suffix to dimension and metrics.
        """
        if projectDict is None:
            raise Exception("require a dictionary")
        self.id: str = projectDict.get("id", "")
        self.name: str = projectDict.get("name", "")
        self.description: str = projectDict.get("description", "")
        self.ownerName: str = projectDict["owner"].get("name", "")
        self.ownerId: int = projectDict["owner"].get("imsUserId", "")
        self.ownerEmail: int = projectDict["owner"].get("login", "")
        self.template: bool = projectDict.get("companyTemplate", False)
        self.type: str = projectDict.get('type',None)
        self.version: str = None
        self.curation: bool = False
        self.reportType:str = None
        if "definition" in projectDict.keys() and projectDict.get('type') == "project":
            definition: dict = projectDict["definition"]
            self.version: str = definition.get("version", None)
            self.curation: bool = definition.get("isCurated", False)
            if definition.get("device", "desktop") != "cell":
                self.reportType = "desktop"
                infos = self._findPanelsInfos(definition["workspaces"][0])
                self.nbPanels: int = infos["nb_Panels"]
                self.nbSubPanels: int = 0
                self.subPanelsTypes: list = []
                for panel in infos["panels"]:
                    self.nbSubPanels += infos["panels"][panel]["nb_subPanels"]
                    self.subPanelsTypes += infos["panels"][panel]["subPanels_types"]
                self.elementsUsed: dict = self._findElements(
                    definition["workspaces"][0], dvIdSuffix=dvIdSuffix
                )
                self.nbElementsUsed: int = (
                    len(self.elementsUsed["dimensions"])
                    + len(self.elementsUsed["metrics"])
                    + len(self.elementsUsed["filters"])
                    + len(self.elementsUsed["calculatedMetrics"])
                )
            else:
                self.reportType = "mobile"
                self.version: str = projectDict.get("definition",{}).get("version", None)
        elif "definition" in projectDict.keys() and projectDict.get('type') == "guidedAnalysis":
            self.reportType = "guidedAnalysis"
            definition: dict = projectDict["definition"]
            self.version: str = definition.get("version", None)
            self.curation: bool = definition.get("isCurated", False)
            self.nbPanels: int = 1
            self.nbSubPanels: int = 1
            self.subPanelsTypes: list = ["Guided Analysis"]
            self.elementsUsed:dict = {
                "metrics" : [met.get('metricId') for met in definition['events']]
            }
            self.elementsUsed['dimensions'] = [dim.get('dimensionId') for met in definition.get('events',[]) for dim in met.get('filters',[])]
            self.elementsUsed['dimensionsItems'] = [dim.get('dimensionItems') for met in definition.get('events',[]) for dim in met.get('filters',[])]
            self.elementsUsed['filters'] = [fil.get('id') for fil in definition['peopleSegments']]
            self.elementsUsed['calculatedMetrics'] = []
            self.elementsUsed["dataViewIds"] = []
            self.elementsUsed["dataViewNames"] = []
            self.nbElementsUsed: int = (
                    len(self.elementsUsed["dimensions"])
                    + len(self.elementsUsed["metrics"])
                    + len(self.elementsUsed["filters"])
                    + len(self.elementsUsed["calculatedMetrics"])
                )
        else:
            self.reportType = projectDict.get('type','unknown')
    def __str__(self) -> str:
        return json.dumps(self.to_dict(), indent=4)

    def __repr__(self) -> str:
        return json.dumps(self.to_dict(), indent=4)

    def _findPanelsInfos(self, workspace: dict = None) -> dict:
        """
        Return a dict of the different information for each Panel.
        Arguments:
            workspace : REQUIRED : the workspace dictionary.
        """
        dict_data = {"workspace_id": workspace["id"]}
        dict_data["nb_Panels"] = len(workspace["panels"])
        dict_data["panels"] = {}
        for panel in workspace["panels"]:
            dict_data["panels"][panel["id"]] = {}
            dict_data["panels"][panel["id"]]["name"] = panel.get("name", "Default Name")
            dict_data["panels"][panel["id"]]["nb_subPanels"] = len(panel["subPanels"])
            dict_data["panels"][panel["id"]]["subPanels_types"] = [
                subPanel["reportlet"]["type"] for subPanel in panel["subPanels"]
            ]
        return dict_data

    def _findElements(self, workspace: dict, dvIdSuffix: bool = False) -> list:
        """
        Returns the list of dimensions used in the FreeformReportlet.
        Arguments :
            workspace : REQUIRED : the workspace dictionary.
        """
        dict_elements: dict = {
            "dimensions": [],
            "dimensionsItems": [],
            "metrics": [],
            "filters": [],
            "dataViewIds": [],
            "calculatedMetrics": [],
            "dataViewNames": [],
        }
        tmp_rsid = ""  # default empty value
        for panel in workspace["panels"]:
            if "reportSuite" in panel.keys():
                dict_elements["dataViewIds"].append(panel["reportSuite"]["id"])
                if dvIdSuffix:
                    tmp_rsid = f"::{panel['reportSuite']['id']}"
                dict_elements["dataViewNames"].append(
                    panel["reportSuite"].get("__metaData__", {}).get("name", "unknown")
                )
            elif "rsid" in panel.keys():
                dict_elements["dataViewIds"].append(panel["rsid"])
                if dvIdSuffix:
                    tmp_rsid = f"::{panel['rsid']}"
            filters: list = panel.get("segmentGroups", [])
            if len(filters) > 0:
                for element in filters:
                    if 'dynamicDimension' in element.keys():
                        typeElement = element["dynamicDimension"]["type"]
                        idElement = element["dynamicDimension"]["id"]
                    else:
                        typeElement = element["componentOptions"][0]["component"]["type"]
                        idElement = element["componentOptions"][0]["component"]["id"]
                    if typeElement == "Segment":
                        dict_elements["filters"].append(idElement)
                    if typeElement == "DimensionItem":
                        clean_id: str = idElement[
                            : idElement.find("::")
                        ]  ## cleaning this type of element : 'variables/evar7.6::3000623228'
                        dict_elements["dimensions"].append(clean_id)
                    if typeElement == "Dimension":
                        dict_elements["dimensions"].append(idElement)
            for subPanel in panel["subPanels"]:
                if subPanel["reportlet"]["type"] == "FreeformReportlet":
                    reportlet = subPanel["reportlet"]
                    rows = reportlet["freeformTable"]
                    if "dimension" in rows.keys():
                        dict_elements["dimensions"].append(
                            f"{rows['dimension']['id']}{tmp_rsid}"
                        )
                    if len(rows["staticRows"]) > 0:
                        for row in rows["staticRows"]:
                            ## I have to get a temp dimension to clean them before loading them in order to avoid counting them multiple time for each rows.
                            temp_list_dim = []
                            componentType: str = row["component"]["type"]
                            if componentType == "DimensionItem":
                                temp_list_dim.append(
                                    f"{row['component']['id']}{tmp_rsid}"
                                )
                            elif (
                                componentType == "Segments"
                                or componentType == "Segment"
                            ):
                                dict_elements["filters"].append(row["component"]["id"])
                            elif componentType == "Metric":
                                dict_elements["metrics"].append(
                                    f"{row['component']['id']}{tmp_rsid}"
                                )
                            elif componentType == "CalculatedMetric":
                                dict_elements["calculatedMetrics"].append(
                                    row["component"]["id"]
                                )
                        if len(temp_list_dim) > 0:
                            temp_list_dim = list(
                                set([el[: el.find("::")] for el in temp_list_dim])
                            )
                        for dim in temp_list_dim:
                            dict_elements["dimensions"].append(f"{dim}{tmp_rsid}")
                    columns = reportlet["columnTree"]
                    for node in columns["nodes"]:
                        temp_data = self._recursiveColumn(node, tmp_rsid=tmp_rsid)
                        dict_elements["calculatedMetrics"] += temp_data[
                            "calculatedMetrics"
                        ]
                        dict_elements["filters"] += temp_data["filters"]
                        dict_elements["metrics"] += temp_data["metrics"]
                        if len(temp_data["dimensionsItems"]) > 0:
                            for dim in set(temp_data["dimensionsItems"]):
                                dict_elements["dimensionsItems"].append(dim)
                        if len(temp_data["dimensions"]) > 0:
                            for dim in set(temp_data["dimensions"]):
                                dict_elements["dimensions"].append(dim)
        dict_elements["metrics"] = list(set(dict_elements["metrics"]))
        dict_elements["filters"] = list(set(dict_elements["filters"]))
        dict_elements["dimensions"] = list(set(dict_elements["dimensions"]))
        dict_elements["calculatedMetrics"] = list(
            set(dict_elements["calculatedMetrics"])
        )
        return dict_elements

    def _recursiveColumn(
        self, node: dict = None, temp_data: dict = None, tmp_rsid: str = ""
    ):
        """
        recursive function to fetch elements in column stack
        tmp_rsid : OPTIONAL : empty by default, if rsid is pass, it will add the value to dimension and metrics
        """
        if temp_data is None:
            temp_data: dict = {
                "dimensions": [],
                "dimensionsItems": [],
                "metrics": [],
                "filters": [],
                "reportSuites": [],
                "calculatedMetrics": [],
            }
        componentType: str = node["component"]["type"]
        if componentType == "Metric":
            temp_data["metrics"].append(f"{node['component']['id']}{tmp_rsid}")
        elif componentType == "CalculatedMetric":
            temp_data["calculatedMetrics"].append(node["component"]["id"])
        elif componentType == "Segment":
            temp_data["filters"].append(node["component"]["id"])
        elif componentType == "DimensionItem":
            dimensionsItem: str = node["component"]["id"]
            new_id: str = dimensionsItem[: dimensionsItem.find("::")]
            temp_data["dimensions"].append(f"{new_id}{tmp_rsid}")
            temp_data["dimensionsItems"].append(dimensionsItem)
        if len(node["nodes"]) > 0:
            for new_node in node["nodes"]:
                temp_data = self._recursiveColumn(
                    new_node, temp_data=temp_data, tmp_rsid=tmp_rsid
                )
        return temp_data

    def to_dict(self) -> dict:
        """
        transform the class into a dictionary
        """
        obj = {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "ownerName": self.ownerName,
            "ownerId": self.ownerId,
            "ownerEmail": self.ownerEmail,
            "template": self.template,
            "reportType": self.reportType,
            "curation": self.curation or False,
            "version": self.version or None,
        }
        add_object = {}
        if hasattr(self, "nbPanels"):
            add_object = {
                "curation": self.curation,
                "version": self.version,
                "nbPanels": self.nbPanels,
                "nbSubPanels": self.nbSubPanels,
                "subPanelsTypes": self.subPanelsTypes,
                "nbElementsUsed": self.nbElementsUsed,
                "dimensions": self.elementsUsed["dimensions"],
                "dimensionsItems": self.elementsUsed["dimensionsItems"],
                "metrics": self.elementsUsed["metrics"],
                "filters": self.elementsUsed["filters"],
                "calculatedMetrics": self.elementsUsed["calculatedMetrics"],
                "dataViewIds": self.elementsUsed["dataViewIds"],
                "dataViewNames": self.elementsUsed["dataViewNames"],
            }
        full_obj = {**obj, **add_object}
        return full_obj
