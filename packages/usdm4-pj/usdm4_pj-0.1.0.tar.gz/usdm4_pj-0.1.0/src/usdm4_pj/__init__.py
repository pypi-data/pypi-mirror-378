import os
import json
from pydantic import BaseModel
from usdm4 import USDM4
from usdm3 import RulesValidationResults
from simple_error_log.errors import Errors
from simple_error_log.error_location import KlassMethodLocation


class USDM4PJ(BaseModel):
    MODULE: str = "src.usdm4_pj.__init__.USDM4PJ"
    _errors: Errors = Errors()
    validation: dict = {}
    success: bool = True
    fatal_error: str = None
    patient_journey: str = ""
    encounters: list = []
    all_activities: list = []
    all_instances: list = []
    all_timings: list = []

    def from_usdm4(self, usdm_path: str, validate: bool = True) -> str | None:
        try:
            location = KlassMethodLocation(self.MODULE, "from_usdm4")
            usdm4 = USDM4()
            if not os.path.exists(usdm_path):
                self.success = False
                self._errors.exception(
                    f"USDM file path does not exist: '{usdm_path}'",
                    location,
                )
                return False
            if validate:
                results: RulesValidationResults = usdm4.validate(usdm_path)
                self.validation = results.to_dict()
                # TODO: Quick fix for managing changes in USDM CT that are not yet updated. So ignoring CT errors belox (DDF00140)
                failures_ids = list(
                    set(
                        [
                            x["rule_id"]
                            for x in self.validation
                            if x["status"] not in ["Not Implemented", "Success"]
                        ]
                    )
                )
                if results.passed_or_not_implemented() or failures_ids == ["DDF00140"]:
                    self._to_patient_journey(usdm_path)
                else:
                    self.success = False
                    self.fatal_error = "USDM v4 validation failed. Check the file using the validate functionality"
            else:
                self._to_patient_journey(usdm_path)
            return self.success

        except Exception as e:
            self.fatal_error = f"Something went wrong {e}"
            self._errors.exception(
                f"Exception raised creating subject journey from usdm4 file '{usdm_path}'",
                e,
                location,
            )
            raise Exception
            return False

    def _to_patient_journey(self, usdm_path):
        with open(usdm_path, "r") as f:
            usdm = json.load(f)

        visits = []
        # encounters
        self.encounters = usdm["study"]["versions"][0]["studyDesigns"][0]["encounters"]

        # activities
        self.all_activities = usdm["study"]["versions"][0]["studyDesigns"][0][
            "activities"
        ]

        # timings
        self.all_timings = []
        for tl in usdm["study"]["versions"][0]["studyDesigns"][0]["scheduleTimelines"]:
            for timing in tl["timings"]:
                self.all_timings.append(timing)

        # instances
        self.all_instances = []
        for tl in usdm["study"]["versions"][0]["studyDesigns"][0]["scheduleTimelines"]:
            for instance in tl["instances"]:
                self.all_instances.append(instance)

        for e in self.encounters:
            print("\nny")
            instances = [x for x in self.all_instances if x["encounterId"] == e["id"]]
            fixed_activities = []
            if instances:
                activityIds = [y for x in instances for y in x["activityIds"]]
                activities = [x for x in self.all_activities if x["id"] in activityIds]
                if len(instances) > 1:
                    # print("e['id']", e['id'])
                    print("activityIds", activityIds)
                    for x in activities:
                        print("x", x["id"])
                fixed_activities = self._get_activities(activities)
            else:
                print("encounter does not have activities", e["id"])

            visit = {}
            visit["title"] = e["label"]
            visit["notes"] = ",".join(e["notes"])
            visit["type"] = ",".join([x["decode"] for x in e["contactModes"]])
            timing = [x for x in self.all_timings if x["id"] == e["scheduledAtId"]]
            print("timings", len(timing))

            if timing:
                visit["timing"] = self._make_timing_text(timing)
                visit["duration"] = timing[0]["value"]
            else:
                visit["timing"] = "none"
                visit["duration"] = "none"
            visit["activities"] = fixed_activities
            visits.append(visit)
            # print("e", e)

        data = {"visits": visits}
        self.patient_journey = json.dumps(data, indent=2)

    def _make_timing_text(self, timing):
        direction = timing[0]["type"]["decode"]
        relation = timing[0]["relativeToFrom"]["decode"]
        relativeTo = [
            x
            for x in self.all_instances
            if x["id"] == timing[0]["relativeToScheduledInstanceId"]
        ]
        print("relativeTo", [x["id"] for x in relativeTo])
        relativeFrom = [
            x
            for x in self.all_instances
            if x["id"] == timing[0]["relativeFromScheduledInstanceId"]
        ]
        print("relativeFrom", [x["id"] for x in relativeFrom])
        if direction == "Before":
            timing_txt = f"'{direction}'  '{relativeTo[0]['label']}'  '{relation}'"
        else:
            timing_txt = f"'{direction}'  '{relativeTo[0]['label']}'  '{relation}'"
        return timing_txt

    def _get_activities(self, activities):
        items = []
        for activity in activities:
            item = {}
            item["title"] = activity["label"]
            if activity["definedProcedures"]:
                procedures = ",".join(
                    [x["label"] for x in activity["definedProcedures"]]
                )
                item["procedures"] = procedures
            else:
                item["procedures"] = ""
            item["notes"] = ",".join(activity["notes"])
            items.append(item)
        return items

    @property
    def errors(self):
        return self._errors
