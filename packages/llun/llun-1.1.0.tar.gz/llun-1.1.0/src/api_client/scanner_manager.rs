use std::collections::HashMap;
use crate::api_client::{AvailableScanner, OpenAiClientError, OpenAiPublicScanner, Response, Scanner, ScannerError};


#[derive(Debug, thiserror::Error)]
pub enum ScannerManagerError {
    #[error("Error in OpenAiClient")]
    OpenAiClientError(#[from] OpenAiClientError),
    #[error("Chosen scanner not found")]
    ScannerNotFound(),
    #[error("Error whilst scanning")]
    ScannerError(#[from] ScannerError)
}

pub struct ScannerManager {
    scanners: HashMap<AvailableScanner, Box<dyn Scanner>>,
}

impl ScannerManager {
    pub fn new() -> Result<Self, ScannerManagerError> {
        let mut scanners: HashMap<AvailableScanner, Box<dyn Scanner>> = HashMap::new();

        scanners.insert(AvailableScanner::OpenAiPublic, Box::new(OpenAiPublicScanner::new()?));

        Ok(Self{ scanners })
    }

    /// use your chosen scanner (its open ai isnt you normie)
    /// to perform a scan
    pub async fn run_scan(&self, system_prompt: &str, user_prompt: &str, model: String, scanner: AvailableScanner) -> Result<Response, ScannerManagerError> {
        let chosen_scanner = self.scanners
            .get(&scanner)
            .ok_or_else(ScannerManagerError::ScannerNotFound)?;
            
        Ok( chosen_scanner.scan_files(system_prompt, user_prompt, model).await? )
    }
}