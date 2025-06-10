// TODO: i18n - processed
import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';import { useTranslation } from "react-i18next";
const LazyExample = () => {const { t } = useTranslation();
  return (
    <Card>
      <CardHeader>
        <CardTitle>{t("components.lazy_loaded_component")}</CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-gray-600">{t("components.this_component_was_loaded_lazily_using_reactlazy_a")}

        </p>
        <div className="mt-4 p-4 bg-gray-100 rounded">
          <code className="text-sm">{t("components.const_lazycomponent_lazy_importlazyexample")}</code>
        </div>
      </CardContent>
    </Card>);

};
export default LazyExample;