from argparse import ArgumentParser
from logging import basicConfig, info, error, debug
from time import time
import datetime as dts
import cv2
from videocapturing import VideoCapture
from multiprocessing import Process, Array


def sub_main(src, cam_idx, backend, running):
    vs = VideoCapture(src, backend)
    video_sizes = vs.get_size()
    now = dts.datetime.utcnow()
    video_writer = cv2.VideoWriter(
        "{}_cam{}.{}".format(
            now.strftime("%Y%m%dT%H%M%S"),
            cam_idx,
            "mp4",
        ),
        cv2.VideoWriter_fourcc(*"mp4v"),
        30.0,
        video_sizes,
        True,
    )
    frame = vs.read_first_frame()
    if frame is not None:
        starttime = time()
        info("Starting thread {}.".format(cam_idx))
        vs.start()
        running[cam_idx] = 1
        while running[cam_idx] == 1:
            starttime = time()
            show = True
            if show:
                cv2.imshow("webcam_{}".format(cam_idx), frame)
            if video_writer.isOpened() and all(
                running
            ):  # wait until all processes are running
                video_writer.write(frame)
                debug("Wrote frame from cam {} to file at {}".format(cam_idx, time()))
            if cv2.waitKey(1) == 27:
                for cam_idx in range(len(running)):
                    running[cam_idx] = 0
                break
            debug("Main loop took {:.2f} ms.".format((time() - starttime) * 1000))
            frame = vs.read()

        # Stop threads
        info("Finished processing. Stopping thread {}.".format(cam_idx))
        vs.stop()
        info("Recorded cameras for {:.2f}s".format((time() - starttime)))
    else:
        info("Could not read data from cam {}.".format(cam_idx))
    video_writer.release()


def main():
    # Video capture
    video_sources = []
    if args.rtsp_cameras:
        for location in args.rtsp_cameras:
            video_sources.append(
                "rtspsrc location={} latency=0 ! rtph264depay ! h264parse ! omxh264dec ! videoconvert ! appsink".format(
                    location
                ).replace(
                    u"\u200b", ""
                )
            )
        backend = cv2.CAP_GSTREAMER
    elif args.rtmp_cameras:
        for location in args.rtmp_cameras:
            video_sources.append(
                "rtmpsrc location={} ! decodebin ! videoconvert ! appsink drop=true max-buffers=1".format(
                    location
                ).replace(
                    u"\u200b", ""
                )
            )
        backend = cv2.CAP_GSTREAMER
    elif args.usb_cameras:
        video_sources = args.usb_cameras
        backend = cv2.CAP_V4L2
    else:
        error("Invalid Camera streaming protocol specified")
        exit()

    camera_count = len(video_sources)
    started = Array(
        "i", [0 for _ in range(camera_count)]
    )  # shared variable between the processes

    info("Stop Recording with 'ESC'")
    processes = [
        Process(
            target=sub_main, args=(video_sources[cam_idx], cam_idx, backend, started)
        )
        for cam_idx in range(camera_count)
    ]
    for cam_idx in range(camera_count):
        processes[cam_idx].start()
    for cam_idx in range(camera_count):
        processes[cam_idx].join()

    cv2.destroyAllWindows()


if __name__ == "__main__":
    parser = ArgumentParser(description="Multi Camera Recording Tool")
    parser.add_argument(
        "--rtsp_cameras",
        type=lambda s: [item.strip() for item in s.split(",")],
        help="Credentials for the webcams; seperated by ','",
    )
    parser.add_argument(
        "--rtmp_cameras",
        type=lambda s: [item.strip() for item in s.split(",")],
        help="Path to webcam devices; seperated by ','",
    )
    parser.add_argument(
        "--usb_cameras",
        type=lambda s: [item.strip() for item in s.split(",")],
        help="Path to webcam devices; seperated by ','",
    )
    args = parser.parse_args()

    basicConfig(format="%(asctime)s %(levelname)s:\t%(message)s", level="INFO")
    main()
