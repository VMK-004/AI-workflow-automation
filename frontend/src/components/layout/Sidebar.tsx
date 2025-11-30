import { FC } from 'react';
import { NavLink } from 'react-router-dom';
import {
  HomeIcon,
  CircleStackIcon,
  RectangleStackIcon,
  ClockIcon,
} from '@heroicons/react/24/outline';
import classNames from 'classnames';

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: HomeIcon },
  { name: 'Workflows', href: '/workflows', icon: RectangleStackIcon },
  { name: 'Vector Collections', href: '/vectors', icon: CircleStackIcon },
  { name: 'Execution History', href: '/runs', icon: ClockIcon },
];

export const Sidebar: FC = () => {
  return (
    <div className="hidden md:flex md:w-64 md:flex-col">
      <div className="flex flex-col flex-grow pt-5 bg-gray-50 overflow-y-auto border-r border-gray-200">
        <div className="mt-5 flex-1 flex flex-col">
          <nav className="flex-1 px-2 space-y-1">
            {navigation.map((item) => (
              <NavLink
                key={item.name}
                to={item.href}
                className={({ isActive }) =>
                  classNames(
                    isActive
                      ? 'bg-primary-100 text-primary-900'
                      : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900',
                    'group flex items-center px-2 py-2 text-sm font-medium rounded-md'
                  )
                }
              >
                {({ isActive }) => (
                  <>
                    <item.icon
                      className={classNames(
                        isActive ? 'text-primary-600' : 'text-gray-400 group-hover:text-gray-500',
                        'mr-3 flex-shrink-0 h-6 w-6'
                      )}
                      aria-hidden="true"
                    />
                    {item.name}
                  </>
                )}
              </NavLink>
            ))}
          </nav>
        </div>
      </div>
    </div>
  );
};

