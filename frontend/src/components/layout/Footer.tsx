export function Footer() {
  const currentYear = new Date().getFullYear()
  
  return (
    <footer className="bg-f1-black text-white py-6 mt-auto">
      <div className="container mx-auto px-4">
        <div className="flex flex-col md:flex-row justify-between items-center">
          <div className="text-sm text-gray-400">
            © {currentYear} F1 Dashboard. Data provided by Jolpica API and OpenF1 API.
          </div>
          <div className="flex space-x-6 mt-4 md:mt-0">
            <a
              href="https://github.com"
              target="_blank"
              rel="noopener noreferrer"
              className="text-gray-400 hover:text-f1-red transition-colors"
            >
              GitHub
            </a>
            <a
              href="https://ergast.com/mrd/"
              target="_blank"
              rel="noopener noreferrer"
              className="text-gray-400 hover:text-f1-red transition-colors"
            >
              Jolpica API
            </a>
            <a
              href="https://openf1.org"
              target="_blank"
              rel="noopener noreferrer"
              className="text-gray-400 hover:text-f1-red transition-colors"
            >
              OpenF1 API
            </a>
          </div>
        </div>
      </div>
    </footer>
  )
}
