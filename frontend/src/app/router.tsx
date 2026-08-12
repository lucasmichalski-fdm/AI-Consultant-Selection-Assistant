import { createBrowserRouter } from "react-router-dom";

import { WorkspacePage } from "@/pages/WorkspacePage";

export const appRouter = createBrowserRouter([
  {
    path: "/",
    element: <WorkspacePage />,
  },
]);
