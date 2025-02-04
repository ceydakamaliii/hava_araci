export function Footer() {
  return (
    <footer className="bg-white border-t">
      <div className="max-w-7xl mx-auto py-4 px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center">
          <div className="text-sm text-gray-500">
            © {new Date().getFullYear()} Aircraft Works
          </div>
          <div className="text-sm text-gray-500">
            Geliştirici: <span className="font-medium">Ceyda Kamalı</span>
          </div>
        </div>
      </div>
    </footer>
  );
}
