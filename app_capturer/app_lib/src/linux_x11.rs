use std::sync::{Arc, Mutex};
use std::{process::Command, thread, time::Duration};
use std::ptr;

use opencv::{core::Size, imgproc, prelude::*};
use x11::xlib::*;

pub fn capture_loop(
    app_name: &str,
    mode: &str,
    stop_flag: Arc<Mutex<bool>>,
    buffer: Arc<Mutex<Option<Vec<u8>>>>,
) {
    const TARGET_WIDTH: i32 = 1920;
    const TARGET_HEIGHT: i32 = 1080;

    unsafe {
        let display = XOpenDisplay(ptr::null());
        if display.is_null() {
            eprintln!("Failed to open X display");
            return;
        }

        let screen = XDefaultScreen(display);
        let root = XRootWindow(display, screen);

        let target_window = if mode == "app" {
            match find_window(app_name) {
                Some(win) => win,
                None => {
                    eprintln!("App '{}' not found. Falling back to root window.", app_name);
                    root
                }
            }
        } else {
            root
        };

        eprintln!("Capturing window: 0x{:x}", target_window);

        let mut attrs: XWindowAttributes = std::mem::zeroed();
        XGetWindowAttributes(display, target_window, &mut attrs);

        let (w, h) = (attrs.width, attrs.height);

        while !*stop_flag.lock().unwrap() {
            let image = XGetImage(display, target_window, 0, 0, w as u32, h as u32, !0, ZPixmap);

            if image.is_null() {
                eprintln!("Failed to get image.");
                thread::sleep(Duration::from_millis(50));
                continue;
            }

            let raw = std::slice::from_raw_parts((*image).data as *const u8, (w * h * 4) as usize);

            // Proper ownership for intermediate Mats
            let flat = Mat::from_slice(raw).unwrap();
            let mat = flat.reshape(4, h).unwrap(); // BGRA

            let mut bgr = Mat::default();
            imgproc::cvt_color(&mat, &mut bgr, imgproc::COLOR_BGRA2BGR, 0).unwrap();

            // Resize to 1920x1080
            let mut resized = Mat::default();
            imgproc::resize(
                &bgr,
                &mut resized,
                Size::new(TARGET_WIDTH, TARGET_HEIGHT),
                0.0,
                0.0,
                imgproc::INTER_LINEAR,
            ).unwrap();

            let data = resized.data_bytes().unwrap().to_vec();
            *buffer.lock().unwrap() = Some(data);

            XDestroyImage(image);
            thread::sleep(Duration::from_millis(33));
        }

        XCloseDisplay(display);
    }
}

unsafe fn find_window(app_name: &str) -> Option<Window> {
    let output = Command::new("wmctrl").arg("-l").output().ok()?;
    let stdout = String::from_utf8_lossy(&output.stdout);

    for line in stdout.lines() {
        let parts: Vec<&str> = line.split_whitespace().collect();
        if parts.len() < 4 {
            continue;
        }

        // Window ID is first column
        let win_id_str = parts[0];
        let title = parts[3..].join(" ");

        if title.to_lowercase().contains(&app_name.to_lowercase()) {
            if let Ok(win_id) = u64::from_str_radix(win_id_str.trim_start_matches("0x"), 16) {
                eprintln!("Found window '{}' with ID 0x{:x}", title, win_id);
                return Some(win_id as Window);
            }
        }
    }

    eprintln!("No window found for app name '{}'", app_name);
    None
}
