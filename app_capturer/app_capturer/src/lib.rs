use libc::c_char;
use once_cell::sync::Lazy;
use std::ffi::CStr;
use std::sync::{Arc, Mutex};
use std::thread;

mod linux_x11;

pub mod api {
    use super::*;

    static STATE: Lazy<Mutex<Option<CapturerHandle>>> = Lazy::new(|| Mutex::new(None));

    struct CapturerHandle {
        stop_flag: Arc<Mutex<bool>>,
        thread: thread::JoinHandle<()>,
        buffer: Arc<Mutex<Option<Vec<u8>>>>,
    }

    #[no_mangle]
    pub extern "C" fn start_capture(app_name: *const c_char, mode: *const c_char) -> bool {
        let app = unsafe { CStr::from_ptr(app_name).to_string_lossy().into_owned() };
        let mode = unsafe { CStr::from_ptr(mode).to_string_lossy().into_owned() };

        let stop_flag = Arc::new(Mutex::new(false));
        let buffer = Arc::new(Mutex::new(None));
        let stop_flag_clone = Arc::clone(&stop_flag);
        let buffer_clone = Arc::clone(&buffer);

        let handle = thread::spawn(move || {
            linux_x11::capture_loop(&app, &mode, stop_flag_clone, buffer_clone);
        });

        let mut state = STATE.lock().unwrap();
        *state = Some(CapturerHandle {
            stop_flag,
            thread: handle,
            buffer,
        });

        true
    }

    #[no_mangle]
    pub extern "C" fn get_frame(buffer: *mut u8, max_len: usize) -> i32 {
        let state = STATE.lock().unwrap();
        if let Some(ref capturer) = *state {
            let buf = capturer.buffer.lock().unwrap();
            if let Some(ref data) = *buf {
                let len = data.len().min(max_len);
                unsafe {
                    std::ptr::copy_nonoverlapping(data.as_ptr(), buffer, len);
                }
                return len as i32;
            }
        }
        -1
    }

    #[no_mangle]
    pub extern "C" fn stop_capture() {
        let mut state = STATE.lock().unwrap();
        if let Some(capturer) = state.take() {
            {
                let mut flag = capturer.stop_flag.lock().unwrap();
                *flag = true;
            }
            capturer.thread.join().unwrap();
        }
    }
}
