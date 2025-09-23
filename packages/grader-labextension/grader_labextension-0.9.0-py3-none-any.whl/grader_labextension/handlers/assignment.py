# Copyright (c) 2022, TU Wien
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

import json
import os

import tornado
from tornado.web import HTTPError, authenticated

from grader_labextension.handlers.base_handler import ExtensionBaseHandler
from grader_labextension.registry import register_handler
from grader_labextension.services.request import RequestService, RequestServiceError


@register_handler(path=r"api\/lectures\/(?P<lecture_id>\d*)\/assignments\/?")
class AssignmentBaseHandler(ExtensionBaseHandler):
    """
    Tornado Handler class for http requests to /lectures/{lecture_id}/assignments.
    """

    @authenticated
    async def get(self, lecture_id: int):
        """Sends a GET request to the grader service and returns assignments of the lecture

        :param lecture_id: id of the lecture
        :type lecture_id: int
        """
        try:
            response = await self.request_service.request(
                method="GET",
                endpoint=f"{self.service_base_url}api/lectures/{lecture_id}/assignments",
                header=self.grader_authentication_header,
                response_callback=self.set_service_headers,
            )

            lecture = await self.request_service.request(
                "GET",
                f"{self.service_base_url}api/lectures/{lecture_id}",
                header=self.grader_authentication_header,
            )
        except RequestServiceError as e:
            self.log.error(e)
            raise HTTPError(e.code, reason=e.message)

        # Create directories for every assignment
        try:
            dirs = set(
                filter(
                    lambda e: e[0] != ".",
                    os.listdir(
                        os.path.expanduser(f"{self.root_dir}/{lecture['code']}/assignments")
                    ),
                )
            )
            for assignment in response:
                if assignment["id"] not in dirs:
                    self.log.info(
                        f"Creating directory {self.root_dir}/{lecture['code']}/assignments/"
                        f"{assignment['id']}"
                    )
                    os.makedirs(
                        os.path.expanduser(
                            f"{self.root_dir}/{lecture['code']}/assignments/{assignment['id']}"
                        ),
                        exist_ok=True,
                    )
                try:
                    dirs.remove(assignment["id"])
                except KeyError:
                    pass
        except FileNotFoundError:
            pass

        self.write(json.dumps(response))

    async def post(self, lecture_id: int):
        """Sends post-request to the grader service to create an assignment

        :param lecture_id: id of the lecture in which the new assignment is
        :type lecture_id: int
        """

        data = tornado.escape.json_decode(self.request.body)
        try:
            response = await self.request_service.request(
                method="POST",
                endpoint=f"{self.service_base_url}api/lectures/{lecture_id}/assignments",
                body=data,
                header=self.grader_authentication_header,
            )

            lecture = await self.request_service.request(
                "GET",
                f"{self.service_base_url}api/lectures/{lecture_id}",
                header=self.grader_authentication_header,
            )
        except RequestServiceError as e:
            self.log.error(e)
            raise HTTPError(e.code, reason=e.message)
        # if we did not get an error when creating the assignment (i.e. the user is authorized
        # etc.) then we can create the directory structure if it does not exist yet
        os.makedirs(
            os.path.expanduser(f"{self.root_dir}/{lecture['code']}/assignments/{response['id']}"),
            exist_ok=True,
        )
        os.makedirs(
            os.path.expanduser(f"{self.root_dir}/{lecture['code']}/source/{response['id']}"),
            exist_ok=True,
        )
        os.makedirs(
            os.path.expanduser(f"{self.root_dir}/{lecture['code']}/release/{response['id']}"),
            exist_ok=True,
        )
        self.write(json.dumps(response))


@register_handler(
    path=r"api\/lectures\/(?P<lecture_id>\d*)\/assignments\/(?P<assignment_id>\d*)\/?"
)
class AssignmentObjectHandler(ExtensionBaseHandler):
    """
    Tornado Handler class for http requests to /lectures/{lecture_id}/assignments/{assignment_id}.
    """

    async def put(self, lecture_id: int, assignment_id: int):
        """Sends a PUT-request to the grader service to update a assignment

        :param lecture_id: id of the lecture
        :type lecture_id: int
        :param assignment_id: id of the assignment
        :type assignment_id: int
        """

        data = tornado.escape.json_decode(self.request.body)
        query_params = RequestService.get_query_string(
            {"recalc-scores": self.get_argument("recalc-scores", None)}
        )
        try:
            response = await self.request_service.request(
                method="PUT",
                endpoint=f"{self.service_base_url}api/lectures/{lecture_id}/assignments/"
                f"{assignment_id}{query_params}",
                body=data,
                header=self.grader_authentication_header,
            )
        except RequestServiceError as e:
            self.log.error(e)
            raise HTTPError(e.code, reason=e.message)
        self.write(json.dumps(response))

    @authenticated
    async def get(self, lecture_id: int, assignment_id: int):
        """Sends a GET-request to the grader service to get a specific assignment

        :param lecture_id: id of the lecture
        :type lecture_id: int
        :param assignment_id: id of the specific assignment
        :type assignment_id: int
        """

        try:
            response = await self.request_service.request(
                method="GET",
                endpoint=f"{self.service_base_url}api/lectures/{lecture_id}/assignments/"
                f"{assignment_id}",
                header=self.grader_authentication_header,
                response_callback=self.set_service_headers,
            )
            lecture = await self.request_service.request(
                "GET",
                f"{self.service_base_url}api/lectures/{lecture_id}",
                header=self.grader_authentication_header,
            )
        except RequestServiceError as e:
            self.log.error(e)
            raise HTTPError(e.code, reason=e.message)

        os.makedirs(
            os.path.expanduser(f"{self.root_dir}/{lecture['code']}/assignments/{response['id']}"),
            exist_ok=True,
        )
        self.write(json.dumps(response))

    async def delete(self, lecture_id: int, assignment_id: int):
        """Sends a DELETE-request to the grader service to "soft"-delete a assignment

        :param lecture_id: id of the lecture
        :type lecture_id: int
        :param assignment_id: id of the assignment
        :type assignment_id: int
        """

        try:
            await self.request_service.request(
                method="DELETE",
                endpoint=f"{self.service_base_url}api/lectures/{lecture_id}/assignments/"
                f"{assignment_id}",
                header=self.grader_authentication_header,
                decode_response=False,
            )
        except RequestServiceError as e:
            raise HTTPError(e.code, reason=e.message)

        self.write({"status": "OK"})


@register_handler(
    path=r"api\/lectures\/(?P<lecture_id>\d*)\/assignments\/(?P<assignment_id>\d*)\/properties\/?"
)
class AssignmentPropertiesHandler(ExtensionBaseHandler):
    """
    Tornado Handler class for http requests to
    /lectures/{lecture_id}/assignments/{assignment_id}/properties.
    """

    @authenticated
    async def get(self, lecture_id: int, assignment_id: int):
        """Sends a GET-request to the grader service and returns the properties of an assignment

        :param lecture_id: id of the lecture
        :type lecture_id: int
        :param assignment_id: id of the assignment
        :type assignment_id: int
        """

        try:
            response = await self.request_service.request(
                method="GET",
                endpoint=f"{self.service_base_url}api/lectures/{lecture_id}/assignments/"
                f"{assignment_id}/properties",
                header=self.grader_authentication_header,
                response_callback=self.set_service_headers,
            )
        except RequestServiceError as e:
            self.log.error(e)
            raise HTTPError(e.code, reason=e.message)
        self.write(response)
