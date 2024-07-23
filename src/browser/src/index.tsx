import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import {createBrowserRouter, RouteObject, RouterProvider} from 'react-router-dom';
import {Header} from './components/pageHeader';
import './assets/css/occassio_style.css';
// import App from './App';
// import reportWebVitals from './reportWebVitals';
import {
    App,
    createDetailLoader,
    createSearchLoader,
    Detail as BrowserDetail,
    Search,
    SearchParams,
    searchUtils
} from '@knaw-huc/browser-base-react';
import {Home} from "./components/home";
import ListItem from "./components/listItem";
import Facets from "./components/facets";
import {Detail} from "./components/detail";

const header = <Header />
const searchLoader = createSearchLoader(searchUtils.getSearchObjectFromParams, '/api/browse', 10);
const detailLoader = createDetailLoader(id => `/api/article?rec=${id}`);
const title = "Occassio";

const routeObject: RouteObject = {
    path: '/',
    element: <App header={header} />,
    children: [
        {index: true, element: <Home />},
        {
            path: "/search",
            loader: async ({request}) => searchLoader(new URL(request.url).searchParams),
            element: <Search pageLength={30} ResultItemComponent={ListItem} FacetsComponent={Facets} withPaging={true} hasIndexPage={false} showSearchHeader={false} updateDocumentTitle={false} searchParams={SearchParams.PARAMS} />
        },
        {
            path: '/detail/:id',
            loader: async ({params}) => detailLoader(params.id as string),
            element: <BrowserDetail title={title} updateDocumentTitle={false} DetailComponent={Detail} />
        }
    ]
}

const root = ReactDOM.createRoot(document.getElementById('root') as HTMLElement);
root.render(
  <React.StrictMode>
      <RouterProvider router={createBrowserRouter([routeObject])} />
  </React.StrictMode>
);
