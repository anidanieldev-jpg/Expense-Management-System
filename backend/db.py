from services.sheets import SheetsService

# Global Singleton instance to avoid re-connecting to Google Sheets in every route
service = SheetsService()
