// TODO: i18n - processed
import { Link } from 'react-router-dom';
/**
 * Footer component for the dashboard layout
 */import { useTranslation } from "react-i18next";
const Footer = () => {const { t } = useTranslation();
  const currentYear = new Date().getFullYear();
  return (
    <footer className="bg-white border-t border-gray-200 py-4">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col md:flex-row justify-between items-center">
          <div className="text-center md:text-left mb-4 md:mb-0">
            <p className="text-sm text-gray-500">
              &copy; {currentYear}{t("components.bdc_beneficiary_development_center_all_rights_rese")}
            </p>
          </div>
          <div className="flex space-x-6">
            <Link to="/privacy-policy" className="text-sm text-gray-500 hover:text-gray-700">{t("components.privacy_policy")}

            </Link>
            <Link to="/terms" className="text-sm text-gray-500 hover:text-gray-700">{t("components.terms_of_service")}

            </Link>
            <Link to="/help" className="text-sm text-gray-500 hover:text-gray-700">{t("components.help")}

            </Link>
          </div>
        </div>
      </div>
    </footer>);

};
export default Footer;