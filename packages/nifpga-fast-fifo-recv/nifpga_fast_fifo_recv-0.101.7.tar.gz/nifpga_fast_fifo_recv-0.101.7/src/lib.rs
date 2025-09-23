extern crate nifpga_dll;

use pyo3::prelude::*;
use pyo3::types::PyDict;
use pyo3::types::PyTuple;

use numpy::{PyArray1};
//use numpy::{PyArray1, PyArray2, PyReadonlyArray1};
// use rayon::prelude::*;


use std::thread;
use std::time::Duration;
use std::sync::{Arc, Mutex};
use crossbeam;
use nifpga_dll::Session;


#[derive(Clone)]
#[pyclass]
struct Configuration {
    bit_file: String,
    signature: String,
    ni_address: String,
    run: bool,
    close_on_reset: bool,
    fifo: u32,
    dma_buffer_size: usize,
    fifo_reading_buffer: usize,
    min_packet: usize,
    delay_us: u64,
    debug: bool
}

fn fpga_loop(conf: &Configuration, tx: &crossbeam::channel::Sender<Vec<u64>>, stop_event: Arc<Mutex<bool>>) {

    let session = Session::open(
        conf.bit_file.as_str(),
        conf.signature.as_str(), //signature from generated header
        conf.ni_address.as_str(),
        conf.run, //run on open
        conf.close_on_reset //close_on_reset on close
    ).unwrap();

    let (reader, depth) = session.open_read_fifo::<u64>(conf.fifo, conf.dma_buffer_size).unwrap();

    println!("Actual DMA FIFO  {} set depth: {} actual depth: {}", conf.fifo, conf.dma_buffer_size, depth);
    println!("conf.fifo_reading_buffer: {}", conf.fifo_reading_buffer);
    println!("debug: {}", conf.debug);

    let mut read_buff:Vec<u64> = Vec::with_capacity(conf.fifo_reading_buffer);
    read_buff.resize(conf.fifo_reading_buffer, 0);

    let mut read_buff_zero_size:Vec<u64> = Vec::with_capacity(0);
    let mut data_available=0;

    let debug = conf.debug;
    // let debug = false;

    // let mut now_time = Instant::now();

    *stop_event.lock().unwrap() = false;

    loop {
        if *stop_event.lock().unwrap() {
            break;
        }

        // let last_time = Instant::now();
        if data_available==0 {
            
            if conf.delay_us>0 {std::thread::sleep(Duration::from_micros(conf.delay_us)); };
            data_available = (reader.read(&mut read_buff_zero_size, 0).unwrap() / conf.min_packet)*conf.min_packet;

            if debug==true {
                if (data_available) > 0 {
                        println!("data_available was 0 now :{}", data_available);
                }
            }

        }

        if data_available>0 {

            if debug==true {
                if (data_available) > 0 {
                        println!("data_available was > 0 now :{}", data_available);
                }
            }

            read_buff.resize((data_available / conf.min_packet)*conf.min_packet, 0);

            let len_data:usize = reader.read(&mut read_buff, conf.fifo_reading_buffer as u32).unwrap();

            if debug==true {
                if (data_available) > 0 {
                        println!("len_data:{}", data_available);
                }
            }

            data_available = (len_data / conf.min_packet)*conf.min_packet;

            if debug==true {
                if (data_available) > 0 {
                        println!("data_available before rounding:{}", data_available);
                }
            }

            if read_buff.len()>0 {
                tx.send(read_buff.to_vec()).unwrap();
                if debug==true {
                    println!("len_data {}", len_data);
                }
            }

        }

        // now_time = Instant::now();
        // let delta_time
        //     = now_time - last_time;

    }

}

/// Reading out from NI FPGA FIFOs with a separate thread allowing fast data-rate in Python.
///
/// It is implemented in Rust and it provides in Python the handle to start a separate thread running
/// a continuously polling loop, store the received data in a queue and reading them asynchronously.
/// This allow to receive data from nifpga in Python without loosing data even for fast data-rate.
///
#[pymodule]
fn nifpga_fast_fifo_recv(m: &Bound<'_, PyModule>) -> PyResult<()> {
    // m.add_function(wrap_pyfunction!(sum_as_string, m)?)?;
    m.add_class::<NifpgaFastFifoRecv>()?;
    Ok(())
}

#[pyclass]
struct NifpgaFastFifoRecv {
    conf: Configuration,
    tx: crossbeam::channel::Sender<Vec<u64>>,
    rx: crossbeam::channel::Receiver<Vec<u64>>,
    thread_handle: Option<std::thread::JoinHandle<()>>,
    stop_event: Arc<Mutex<bool>>,
}

///provaC
#[pymethods]
impl NifpgaFastFifoRecv {
    ///Create a new NifpgaFastFifoRecv
    ///NifpgaFastFifoRecv(bitfile, signature, run, close_on_reset, fifo, dma_buffer_size,
    ///fifo_reading_buffer, fifo_buffer_size)
    #[new]
    #[pyo3(signature = (bitfile = "X", signature = "ABCD12345678", ni_address = "RI0", run = false, close_on_reset = false, fifo = 0, dma_buffer_size=50000, fifo_reading_buffer=10000, min_packet=1, delay_us = 0, debug = false))]
    fn new(bitfile: &str,
           signature: &str,
           ni_address:  &str,
           run: bool,
           close_on_reset: bool,
           fifo: u32,
           dma_buffer_size: usize,
           fifo_reading_buffer: usize,
           min_packet: usize,
           delay_us: u64,
           debug: bool) -> Self {

        let (tx, rx) = crossbeam::channel::unbounded();
        NifpgaFastFifoRecv { conf: Configuration{bit_file:String::from(bitfile),
                                                 signature:String::from(signature),
                                                 ni_address:String::from(ni_address),
                                                 run,
                                                 close_on_reset,
                                                 fifo,
                                                 dma_buffer_size,
                                                 fifo_reading_buffer,
                                                 min_packet,
                                                 delay_us,
                                                 debug},
                  tx: tx,
                  rx: rx,
                  thread_handle: None::<std::thread::JoinHandle<()>>,
                  stop_event: Arc::new(Mutex::new(false)),
        }
    }

    ///thread_start run the thread
    fn thread_start(&mut self, _py: Python<'_>) -> PyResult<()> {
        println!("Start two threads.");
        let conf_local = self.conf.clone();
        let tx_local = self.tx.clone();
        let stop_event = self.stop_event.clone();

        match &self.thread_handle {
            Some(_x)=>{
                eprintln!("THREAD ALREADY EXITS")
            },
            None=>{
                let handle = thread::spawn(move || {
                //fpga_loop_dummy(&conf_local, &tx_local, stop_event);
                fpga_loop(&conf_local, &tx_local, stop_event)
                });

                println!("Thread started!");

                self.thread_handle = Some(handle);
            },
        };

        Ok(())
    }

    ///thread_is_running return true is thread is running
    ///
    /// returns a bool (PyO3 will convert to Python bool)
    fn thread_is_running(&mut self) -> PyResult<bool> {
        let status = match &self.thread_handle {
            Some(_x)=>{
                true
            },
            None=>{
                false
            },
        };
        Ok(status)
    }

    ///thread_stop stop the thread
    fn thread_stop(&mut self, _py: Python<'_>) -> PyResult<()> {
        *self.stop_event.lock().unwrap() = true;
        println!("stop_event True");

        if let Some(handle) = self.thread_handle.take() {
           handle.join().expect("failed to join thread");
        }
        else {
            eprintln!("THREAD DO NOT EXITS");
        }

        self.thread_handle = None::<std::thread::JoinHandle<()>>;

        // match th {
        println!("stop_event True done");
        Ok(())
    }


    fn get_data(&mut self) -> PyResult<Vec<u64>> {
        self.get_data_as_list()
    }
    
    // /// Get data as a NumPy array    
    fn get_data_as_numpy<'py>(&mut self, py: Python<'py>) -> PyResult<Py<PyArray1<u64>>> {
        let debug = self.conf.debug;
        
        // Pre-allocate with estimated capacity to reduce reallocations
        let mut combined: Vec<u64> = Vec::new();
        
        // Collect all items efficiently
        while let Ok(item) = self.rx.try_recv() {
            combined.extend(item);
        }
        
        if debug {
            println!("combined.len() = {}", combined.len());
        }
        
        // Zero-copy: transfer ownership directly to NumPy without cloning
        let array = PyArray1::from_vec(py, combined);
        Ok(array.into())
    }



    /// Get data as a Python tuple
    fn get_data_as_ntuple<'py>(&mut self, py: Python<'py>) -> PyResult<Py<PyTuple>> {
        let debug = self.conf.debug;
        let mut combined: Vec<u64> = Vec::new();

        while let Ok(item) = self.rx.try_recv() {
            combined.extend(item);
        }

        if debug {
            println!("combined.len() = {}", combined.len());
        }

        // PyTuple::new returns Result<Bound<PyTuple>, PyErr>, so unwrap it via ? first
        let tuple = PyTuple::new(py, combined)?;
        Ok(tuple.into()) // now we can convert Bound<PyTuple> -> Py<PyTuple>
    }

    /// Get data from the internal queue
    ///
    /// Drains the channel directly into a single Vec<u64>
    /// Returns a Python list of ints (PyO3 will convert automatically)
    fn get_data_as_list(&mut self) -> PyResult<Vec<u64>> {
        let debug = self.conf.debug;
        let mut combined: Vec<u64> = Vec::new();

        // Drain the channel directly into a single vector
        while let Ok(item) = self.rx.try_recv() {
            combined.extend(item); // assuming item: Vec<u64>
        }

        if debug {
            println!("combined.len() = {}", combined.len());
        }

        Ok(combined) // PyO3 converts Vec<u64> -> Python list automatically
    }

    ///get the current configuration
    /// returns a Python dict with all configuration fields
    fn get_conf(&mut self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        let d = PyDict::new(py);

        d.set_item("bit_file", &self.conf.bit_file)?;
        d.set_item("signature", &self.conf.signature)?;
        d.set_item("ni_address", &self.conf.ni_address)?;
        d.set_item("run", self.conf.run)?;
        d.set_item("close_on_reset", self.conf.close_on_reset)?;
        d.set_item("fifo", self.conf.fifo)?;
        d.set_item("dma_buffer_size", self.conf.dma_buffer_size)?;
        d.set_item("fifo_reading_buffer", self.conf.fifo_reading_buffer)?;
        d.set_item("delay_us", self.conf.delay_us)?;
        d.set_item("min_packet", self.conf.min_packet)?;

        Ok(d.into())
    }

    ///get the current configuration
    ///
    /// returns a tuple:
    /// (bit_file, signature, ni_address, run, close_on_reset, fifo, dma_buffer_size, fifo_reading_buffer, delay_us, min_packet)
    /// Python callers can unpack or convert to dict as they prefer.
    fn get_conf_as_tuple(&mut self) -> PyResult<(String, String, String, bool, bool, u32, usize, usize, u64, usize)> {
        Ok((
            self.conf.bit_file.clone(),
            self.conf.signature.clone(),
            self.conf.ni_address.clone(),
            self.conf.run,
            self.conf.close_on_reset,
            self.conf.fifo,
            self.conf.dma_buffer_size,
            self.conf.fifo_reading_buffer,
            self.conf.delay_us,
            self.conf.min_packet,
        ))
    }

}
