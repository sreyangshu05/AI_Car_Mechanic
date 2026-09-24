import './styles.css';
import type { ReactNode } from 'react';
export const metadata={title:'AI Car Mechanic',description:'Practical vehicle troubleshooting'};
export default function Layout({children}:{children:ReactNode}){return <html lang="en" suppressHydrationWarning><body className="mechanic-app">{children}</body></html>}
