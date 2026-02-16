import { render, screen } from "@testing-library/react";
import "@testing-library/jest-dom";

jest.mock("next/navigation", () => ({
  usePathname: () => "/",
}));

jest.mock("next/link", () => {
  return function MockLink({ children, href }: { children: React.ReactNode; href: string }) {
    return <a href={href}>{children}</a>;
  };
});

import Sidebar from "@/components/Sidebar";

describe("Sidebar", () => {
  it("renders navigation links", () => {
    render(<Sidebar />);
    expect(screen.getByText("Puffling")).toBeInTheDocument();
    expect(screen.getByText("Dashboard")).toBeInTheDocument();
    expect(screen.getByText("Backtest")).toBeInTheDocument();
    expect(screen.getByText("Strategies")).toBeInTheDocument();
    expect(screen.getByText("AI Chat")).toBeInTheDocument();
    expect(screen.getByText("Data")).toBeInTheDocument();
    expect(screen.getByText("Trades")).toBeInTheDocument();
    expect(screen.getByText("Settings")).toBeInTheDocument();
  });

  it("has 7 navigation links", () => {
    render(<Sidebar />);
    const links = screen.getAllByRole("link");
    expect(links).toHaveLength(7);
  });
});
