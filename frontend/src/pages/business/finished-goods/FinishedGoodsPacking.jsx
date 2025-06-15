import React from 'react';
import { Card, Typography } from 'antd';
import styled from 'styled-components';
const { Title } = Typography;
const StyledCard = styled(Card)`border-radius: 8px; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08); border: none;`;
const SectionTitle = styled(Title)`position: relative; margin-bottom: 24px !important; font-weight: 600 !important; &::after { content: ''; position: absolute; bottom: -8px; left: 0; width: 48px; height: 3px; background: #1890ff; border-radius: 2px; }`;
export default () => <div><SectionTitle level={4}>成品打包</SectionTitle><StyledCard><p>成品打包功能正在开发中...</p></StyledCard></div>; 