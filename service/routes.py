"""
Account Service

This microservice handles the lifecycle of Accounts
"""
# pylint: disable=unused-import
from flask import jsonify, request, make_response, abort, url_for  # noqa; F401
from service.models import Account
from service.common import status  # HTTP Status Codes
from . import app  # Import Flask application


############################################################
# Health Endpoint
############################################################
@app.route("/health")
def health():
    """Health Status"""
    return jsonify(dict(status="OK")), status.HTTP_200_OK


@app.route("/internal-server-error")
def test_for_internal_server_error_handler():
    abort(500)


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    return (
        jsonify(
            name="Account REST API Service",
            version="1.0",
            # paths=url_for("list_accounts", _external=True),
        ),
        status.HTTP_200_OK,
    )


######################################################################
# CREATE A NEW ACCOUNT
######################################################################
@app.route("/accounts", methods=["POST"])
def create_accounts():
    """
    Creates an Account
    This endpoint will create an Account based the data in the body that is posted
    """
    app.logger.info("Request to create an Account")
    check_content_type("application/json")
    account = Account()
    account.deserialize(request.get_json())
    account.create()
    message = account.serialize()
    # Uncomment once get_accounts has been implemented
    # location_url = url_for("get_accounts", account_id=account.id, _external=True)
    location_url = "/"  # Remove once get_accounts has been implemented
    return make_response(
        jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}
    )


######################################################################
# LIST ALL ACCOUNTS
######################################################################
@app.route("/accounts", methods=["GET"])
def list_accounts():
    """
    Returns a list of all Accounts
    This endpoint will create an Account based the data in the body that is posted
    """
    app.logger.info("Request for listing all Accounts")
    accounts = Account.all()
    accounts = [] if not accounts else [each.serialize() for each in accounts]
    app.logger.info(f"Returning {len(accounts)} Accounts")
    return make_response(jsonify(accounts), status.HTTP_200_OK)


######################################################################
# READ AN ACCOUNT
######################################################################
@app.route("/accounts/<account_id>", methods=["GET"])
def get_account(account_id):
    """
    Returns an Account
    This endpoint will query an Account matching the account id passed
    """
    app.logger.info("Request for getting an Account's info")
    account = Account.find(by_id=account_id)
    res_payload = account if not account else account.serialize()
    if not account:
        abort(status.HTTP_404_NOT_FOUND)
    return make_response(
        jsonify(res_payload),
        status.HTTP_200_OK,
    )


######################################################################
# UPDATE AN EXISTING ACCOUNT
######################################################################
@app.route("/accounts/<int:account_id>", methods=["PUT"])
def update_account_info(account_id):
    """
    Update an Account's info
    This endpoint will update the Account's info based on the payload passed
    returns the updated account after saving the changes
    """
    app.logger.info(f"Request for updating an account {account_id=}")
    check_content_type("application/json")
    account = Account.find(by_id=account_id)
    if not account:
        abort(404, f"Account with {account_id=} not found")
    payload: dict = request.get_json()  # type: ignore
    if "id" in payload:
        abort(400, f"ID is cannot be changed")
    account.deserialize(payload)
    account.update()
    return account.serialize(), status.HTTP_200_OK


######################################################################
# DELETE AN ACCOUNT
######################################################################
@app.route("/accounts/<int:account_id>", methods=["DELETE"])
def delete_account(account_id):
    """
    Deletes an Account
    This endpoint will update the Account's info based on the payload passed
    returns the updated account after saving the changes
    """
    account = Account.find(by_id=account_id)
    if not account:
        return make_response(
            jsonify({"detail": "not found"}, status.HTTP_404_NOT_FOUND)
        )
    # delete the account
    account.delete()
    return make_response("", status.HTTP_204_NO_CONTENT)


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################


def check_content_type(media_type):
    """Checks that the media type is correct"""
    content_type = request.headers.get("Content-Type")
    if content_type and content_type == media_type:
        return
    app.logger.error("Invalid Content-Type: %s", content_type)
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        f"Content-Type must be {media_type}",
    )
