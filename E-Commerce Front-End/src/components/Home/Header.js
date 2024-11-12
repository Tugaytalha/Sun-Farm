import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import './Home.css';
import { Menu, Dropdown, Button } from 'antd';
import { FaShoppingCart, FaBox } from 'react-icons/fa';
import { UserOutlined, AccountBookOutlined, PlusOutlined, HeartOutlined } from '@ant-design/icons';
import CategoryApiService from '../../services/CategoryApiService';

const Header = () => {
    const navigate = useNavigate();
    const [menuVisible, setMenuVisible] = useState(false);
    const [logoImage, setLogoImage] = useState('');

    useEffect(() => {
        const fetchLogoImage = async () => {
            try {
                const responseLogo = await CategoryApiService.getLogo();
                setLogoImage(responseLogo.data);
            } catch (error) {
                console.error('Error fetching logo:', error);
            }
        };
        fetchLogoImage();
    }, [navigate]);

    const isUserLoggedIn = () => {
        return localStorage.getItem('authToken') !== null;
    };

    const handleMenuClickWhenLogOut = (e) => {
        if (e.key === 'login') {
            navigate('/login');
        } else if (e.key === 'signup') {
            navigate('/register');
        }
    };

    const handleMenuClickWhenLogIn = (e) => {
        if (e.key === 'account-info') {
            navigate('/user-info');
        } else if (e.key === 'my-orders') {
            navigate('/list-orders');
        } else if (e.key === 'logout') {
            localStorage.removeItem('authToken');
            navigate('/');
        }
    };

    const handleFavoritesNavigation = () => {
        navigate('/favorite');
    };

    const menu = (
        <Menu onClick={handleMenuClickWhenLogOut}>
            <Menu.Item key="login">Sign In</Menu.Item>
            <Menu.Item key="signup">Sign Up</Menu.Item>
        </Menu>
    );

    const accountMenu = (
        <Menu onClick={handleMenuClickWhenLogIn}>
            <Menu.Item key="account-info">Hesap Bilgisi</Menu.Item>
            <Menu.Item key="my-orders">Siparişlerim</Menu.Item>
            <Menu.Item key="logout">Çıkış</Menu.Item>
        </Menu>
    );

    return (
        <header className="home-header">
            <div className="logo-container">
                <Link to="/">
                    <img src={logoImage} alt="Logo" className="logo" />
                </Link>
            </div>

            {isUserLoggedIn() ? (
                <Dropdown
                    overlay={accountMenu}
                    trigger={['click']}
                    visible={menuVisible}
                    onVisibleChange={(flag) => setMenuVisible(flag)}
                >
                    <Button
                        type="text"
                        icon={<UserOutlined />}
                        onClick={(e) => e.preventDefault()}
                        style={{ color: 'white' }}
                    >
                        Hesabım
                    </Button>
                </Dropdown>
            ) : (
                <Dropdown
                    overlay={menu}
                    trigger={['click']}
                    visible={menuVisible}
                    onVisibleChange={(flag) => setMenuVisible(flag)}
                >
                    <Button
                        type="text"
                        icon={<UserOutlined />}
                        onClick={(e) => e.preventDefault()}
                        style={{ color: 'white' }}
                    >
                        Sign In
                    </Button>
                </Dropdown>

            )
            
            }
               {<Button
                type="text"
                /*</header>icon={<FaShoppingCart />}*/
                onClick={() => navigate('/production')}
                style={{ color: 'white' }}
            >
                Üretim Hesapla
            </Button>

            }
            <Button
                type="text"
                icon={<HeartOutlined />}
                onClick={handleFavoritesNavigation}
                style={{ color: 'white' }}
            >
                Favoriler
            </Button>
            {/* <Button
                type="text"
                icon={<PlusOutlined />}
                onClick={() => navigate('/add-product')}
                style={{ color: 'white' }}
            >
                Add Product
            </Button>
            <Button
                type="text"
                icon={<FaBox />}
                onClick={() => navigate('/update-product')}
                style={{ color: 'white' }}
            >
                My Products
            </Button> */}
            <Button
                type="text"
                icon={<FaShoppingCart />}
                onClick={() => navigate('/cart')}
                style={{ color: 'white' }}
            >
                Sepetim
            </Button>
            
        </header>
    );
};

export default Header;
