use std::ffi::CString;
use std::thread;
use std::time::Duration;

use app_capturer::api::{start_capture, get_frame, stop_capture};

fn main() {
    let app = CString::new("Google Chrome").unwrap();
    let mode = CString::new("app").unwrap(); // or "full_screen"

    let started = start_capture(app.as_ptr(), mode.as_ptr());
    if !started {
        println!("Failed to start capture");
        return;
    }

    println!("Started capture — waiting for frames...");

    let mut buffer = vec![0u8; 1920 * 1080 * 3]; // Adjust if needed

    for i in 0..60 {
        let size = get_frame(buffer.as_mut_ptr(), buffer.len());
        if size > 0 {
            println!("Frame {} captured: {} bytes", i, size);
        } else {
            println!("No frame available");
        }
        thread::sleep(Duration::from_millis(100));
    }

    stop_capture();
    println!("Capture stopped.");
}
