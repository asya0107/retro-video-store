from app import db
from app.models.customer import Customer
from app.models.video import Video
from app.models.rental import Rental
from flask import Blueprint, jsonify, request, make_response
import requests
from datetime import datetime, timedelta


videos_bp = Blueprint("videos", __name__, url_prefix="/videos")


@videos_bp.route("", methods=["POST"])
def create_video():
    request_body = request.get_json()

    if "title" not in request_body:
        return jsonify({"details": "Request body must include title."}), 400
    if "release_date" not in request_body:
        return jsonify({"details": "Request body must include release_date."}), 400
    if "total_inventory" not in request_body:
        return jsonify({"details": "Request body must include total_inventory."}), 400

    new_video = Video(
        title=request_body["title"],
        release_date=request_body["release_date"],
        total_inventory=request_body["total_inventory"],
    )
    db.session.add(new_video)
    db.session.commit()

    response_body = {


        "id": new_video.video_id,
        "title": new_video.title,
        "release_date": new_video.release_date,
        "total_inventory": new_video.total_inventory,

    }

    return jsonify(response_body), 201


@videos_bp.route("", methods=["GET"])
def get_videos():
    videos = Video.query.all()
    video_response = []

    for video in videos:
        video_response.append({
            "id": video.video_id,
            "title": video.title,
            "release_date": video.release_date,
            "total_inventory": video.total_inventory
        })
    return jsonify(video_response)


@videos_bp.route("/<video_id>", methods=["GET"])
def get_one_video(video_id):

    # customer = Customer.query.get_or_404(customer_id)
    if video_id.isnumeric() != True:
        return jsonify({"error": "Invalid Data"}), 400

    video = Video.query.get(video_id)

    if video is None:
        return {"message": f"Video {video_id} was not found"}, 404
        # refactor with helper function
    response_body = {
        "id": video.video_id,
        "title": video.title,
        "release_date": video.release_date,
        "total_inventory": video.total_inventory
    }
    return jsonify(response_body), 200


@videos_bp.route("/<video_id>", methods=["PUT"])
def update_one_video(video_id):
    video = Video.query.get(video_id)
    request_body = request.get_json()

    if video is None:
        return {"message": f"Video {video_id} was not found"}, 404

    if "title" not in request_body:
        return make_response("", 400)
    if "release_date" not in request_body:
        return make_response("", 400)
    if "total_inventory" not in request_body:
        return make_response("", 400)

    video.title = request_body["title"]
    video.release_date = request_body["release_date"]
    video.total_inventory = request_body["total_inventory"]

    db.session.add(video)
    db.session.commit()

    response_body = {
        "id": video.video_id,
        "title": video.title,
        "release_date": video.release_date,
        "total_inventory": video.total_inventory
    }

    return jsonify(response_body), 200


@videos_bp.route("/<video_id>", methods=["DELETE"])
def delete_one_video(video_id):
    video = Video.query.get(video_id)

    if video is None:
        return {"message": f"Video {video_id} was not found"}, 404

    db.session.delete(video)
    db.session.commit()

    return {"id": video.video_id}


@videos_bp.route("/<video_id>/rentals", methods=["GET"])
def customers_with_video(video_id):
    if video_id.isnumeric() != True:
        return jsonify({"error": "Invalid Data"}), 400

    video = Video.query.get(video_id)

    if video is None:
        return {"message": f"Video {video_id} was not found"}, 404

    rentals = Rental.query.filter_by(
        video_id=video.video_id, videos_checked_in=False)

    response_body = list()

    for rental in rentals:
        customer = Customer.query.get(rental.customer_id)

        response_body.append(
            {
                "due_date": rental.due_date,
                "name": customer.name,
                "phone": customer.phone,
                "postal_code": customer.postal_code})

    return jsonify(response_body), 200
