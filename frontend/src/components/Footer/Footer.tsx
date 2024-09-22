import { Github, Linkedin, Mail, Globe } from 'lucide-react';

const Footer = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-gray-950 w-full py-12 mt-16 text-white">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div>
            <h3 className="text-lg font-semibold mb-4">About</h3>
            <p className="text-sm text-gray-400">
              Independent developer and researcher passionate about creating solutions.
            </p>
          </div>
          <div>
            <h3 className="text-lg font-semibold mb-4">Quick Links</h3>
            <ul className="space-y-2">
              <li><a href="/about" className="text-sm text-gray-400 hover:text-white">About Me</a></li>
              <li><a href="/projects" className="text-sm text-gray-400 hover:text-white">Projects</a></li>
            </ul>
          </div>
          <div>
            <h3 className="text-lg font-semibold mb-4">Connect</h3>
            <div className="flex space-x-4">
              <a href="https://github.com/bananya-ml" className="text-gray-400 hover:text-white">
                <Github size={20} />
              </a>
              <a href="https://linkedin.com/in/bhatnagarananya" className="text-gray-400 hover:text-white">
                <Linkedin size={20} />
              </a>
              <a href="mailto:bhatnagarananya64@outlook.com" className="text-gray-400 hover:text-white">
                <Mail size={20} />
              </a>
              <a href="https://ananyabhatnagar.vercel.app" className="text-gray-400 hover:text-white">
                <Globe size={20} />
              </a>
            </div>
          </div>
        </div>
        <div className="mt-8 pt-8 border-t border-gray-800 text-sm text-gray-400">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <p>&copy; {currentYear} Ananya Bhatnagar. All rights reserved.</p>
            <p className="mt-2 md:mt-0">App Version 0.2.0</p>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;