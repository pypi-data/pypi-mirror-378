//#![allow(unused)]
//use csv;
//
//pub struct RBConfig {
//    pub rat_id_arr: Vec<u8>,
//    pub ltb_id_arr: Vec<u8>,
//    pub rb1_id_arr: Vec<u8>,
//    pub rb2_id_arr: Vec<u8>,
//    pub pb_id_arr: Vec<u8>,
//}
//
//impl RBConfig {
//    pub fn new() -> Self {
//        let rb_config_csv = include_str!("../config/nts_config.csv");
//        let mut reader = csv::ReaderBuilder::new()
//            .comment(Some(b'#'))
//            .escape(Some(b'\\'))
//            .flexible(true)
//            .from_reader(rb_config_csv.as_bytes());
//
//        let mut rat_id_arr: Vec<u8> = Vec::new();
//        let mut ltb_id_arr: Vec<u8> = Vec::new();
//        let mut rb1_id_arr: Vec<u8> = Vec::new();
//        let mut rb2_id_arr: Vec<u8> = Vec::new();
//        let mut pb_id_arr: Vec<u8> = Vec::new();
//
//        for (i, record) in reader.records().enumerate() {
//            let record = record.expect("failed to convert record");
//            let rat_id = &record[0].parse::<u8>().unwrap();
//            let ltb_id = &record[1].parse::<u8>().unwrap();
//            let rb1_id = &record[2].parse::<u8>().unwrap();
//            let rb2_id = &record[3].parse::<u8>().unwrap();
//            let pb_id = &record[4].parse::<u8>().unwrap();
//
//            rat_id_arr.push(*rat_id);
//            ltb_id_arr.push(*ltb_id);
//            rb1_id_arr.push(*rb1_id);
//            rb2_id_arr.push(*rb2_id);
//            pb_id_arr.push(*pb_id);
//
//            // println!("{}, {}, {}, {}, {}", rat_id, ltb_id, rb1_id, rb2_id, pb_id);
//        }
//
//        Self {
//            rat_id_arr,
//            ltb_id_arr,
//            rb1_id_arr,
//            rb2_id_arr,
//            pb_id_arr,
//        }
//    }
//}
//// pub fn rb_config_read() {
////     let rb_config_csv = include_str!("../config/nts_config.csv");
////     let mut reader = csv::ReaderBuilder::new()
////         .comment(Some(b'#'))
////         .escape(Some(b'\\'))
////         .flexible(true)
////         .from_reader(rb_config_csv.as_bytes());
//
////     let mut rat_id_arr: Vec<u8> = Vec::new();
////     let mut ltb_id_arr: Vec<u8> = Vec::new();
////     let mut rb1_id_arr: Vec<u8> = Vec::new();
////     let mut rb2_id_arr: Vec<u8> = Vec::new();
////     let mut pb_id_arr: Vec<u8> = Vec::new();
//
////     for (i, record) in reader.records().enumerate() {
////         let record = record.expect("failed to convert record");
////         let rat_id = &record[0].parse::<u8>().unwrap();
////         let ltb_id = &record[1].parse::<u8>().unwrap();
////         let rb1_id = &record[2].parse::<u8>().unwrap();
////         let rb2_id = &record[3].parse::<u8>().unwrap();
////         let pb_id = &record[4].parse::<u8>().unwrap();
//
////         rat_id_arr.push(*rat_id);
////         ltb_id_arr.push(*ltb_id);
////         rb1_id_arr.push(*rb1_id);
////         rb2_id_arr.push(*rb2_id);
////         pb_id_arr.push(*pb_id);
//
////         // println!("{}, {}, {}, {}, {}", rat_id, ltb_id, rb1_id, rb2_id, pb_id);
////     }
////     println!("{:?}", rat_id_arr);
////     println!("{:?}", ltb_id_arr);
////     println!("{:?}", rb1_id_arr);
////     println!("{:?}", rb2_id_arr);
////     println!("{:?}", pb_id_arr);
//// }
