import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import {createHashRouter, RouteObject, RouterProvider, useRouteError} from 'react-router-dom';
import './assets/css/occassio_style.scss';
import {
    App,
    createDetailLoader,
    createSearchLoader,
    Detail as BrowserDetail, // initBrowserBase,
    Search,
    SearchParams,
    searchUtils
} from '@knaw-huc/browser-base-react';
import ListItem from "./components/listItem";
import Facets from "./components/facets";
import {Detail} from "./components/detail";
import {BASE_API_URL} from "./misc/config.ts";
// import i18next from "i18next";
// import {initReactI18next} from "react-i18next";
import {Header} from "./components/pageHeader.tsx";

const header = <Header />
const searchLoader = createSearchLoader(searchUtils.getSearchObjectFromParams, BASE_API_URL + '/api/browse', 10);
const detailLoader = createDetailLoader(id => BASE_API_URL + `/api/article?rec=${id}`);
const title = "Occassio";

const routeObject: RouteObject = {
    path: '/',
    element: <App header={header} />,
    children: [
        // {index: true, element: <Home />},
        {
            // path: '/search',
            index: true,
            loader: async ({request}) => searchLoader(new URL(request.url).searchParams),
            element: <Search pageLength={30} ResultItemComponent={ListItem} FacetsComponent={Facets} withPaging={true} hasIndexPage={false} showSearchHeader={false} updateDocumentTitle={false} searchParams={SearchParams.PARAMS} />,
            errorElement: <ErrorBoundary />,
        },
        {
            path: '/detail/:id',
            loader: async ({params}) => detailLoader(params.id as string),
            element: <BrowserDetail title={title} updateDocumentTitle={false} DetailComponent={Detail} />,
            errorElement: <ErrorBoundary />,
        }
    ],
    errorElement: <ErrorBoundary />,
}

function ErrorBoundary() {
    let error = useRouteError()
    console.error(error)
    return <h1>Error loading page</h1>
}

// i18next.use(initReactI18next).init({
//     lng: "nl"
// }).then(() => {initBrowserBase()})

// initBrowserBase({lang: 'en'})

const root = ReactDOM.createRoot(document.getElementById('root') as HTMLElement);
root.render(
  <React.StrictMode>
      <RouterProvider router={createHashRouter([routeObject])} />
  </React.StrictMode>
);
